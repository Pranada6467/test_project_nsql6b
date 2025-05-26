import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from config.config import MODEL_CONFIG, FEW_SHOT_CONFIG, PERFORMANCE_CONFIG
from utils.example_selector import select_relevant_examples
from utils.query_optimizer import optimize_schema_context, validate_sql_syntax
from utils.query_cache import query_cache
import logging

# Set up logging
logging.basicConfig(level=getattr(logging, PERFORMANCE_CONFIG['logging_level']))
logger = logging.getLogger(__name__)

def load_model():
    """Load model and tokenizer with proper quantization config"""
    logger.info(f"Loading model: {MODEL_CONFIG['model_name']}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_CONFIG['model_name'])
        
        # Set pad token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model_kwargs = {
            'device_map': MODEL_CONFIG['device'],
            'torch_dtype': torch.float16,
        }
        
        # Use new BitsAndBytesConfig instead of deprecated load_in_8bit
        if MODEL_CONFIG.get('use_8bit', False):
            try:
                # Check if bitsandbytes is properly installed
                import bitsandbytes as bnb
                logger.info(f"bitsandbytes version: {bnb.__version__}")
                
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0,
                    llm_int8_has_fp16_weight=False,
                )
                model_kwargs['quantization_config'] = quantization_config
                logger.info("Using 8-bit quantization with BitsAndBytesConfig")
                
            except ImportError as e:
                logger.warning(f"bitsandbytes not available: {e}")
                logger.warning("Loading model without quantization")
                MODEL_CONFIG['use_8bit'] = False
            except Exception as e:
                logger.warning(f"Error setting up quantization: {e}")
                logger.warning("Loading model without quantization")
                MODEL_CONFIG['use_8bit'] = False
        
        # Load model with error handling
        try:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_CONFIG['model_name'],
                **model_kwargs
            )
            logger.info(f"Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading with quantization: {e}")
            logger.info("Attempting to load without quantization...")
            
            # Fallback: load without quantization
            fallback_kwargs = {
                'device_map': MODEL_CONFIG['device'],
                'torch_dtype': torch.float16,
            }
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_CONFIG['model_name'],
                **fallback_kwargs
            )
            logger.info("Model loaded successfully without quantization")
        
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

# Only load model when this module is imported by other modules
# This prevents loading during app startup if there are issues
model = None
tokenizer = None

def get_model():
    """Lazy loading of model and tokenizer"""
    global model, tokenizer
    if model is None or tokenizer is None:
        model, tokenizer = load_model()
    return model, tokenizer

# Rest of your functions with lazy loading...
def generate_sql(question: str, schema: str, use_few_shot: bool = None) -> str:
    """Generate SQL query from natural language question"""
    try:
        # Get model and tokenizer (lazy loading)
        model, tokenizer = get_model()
        
        # Use configuration default if not specified
        if use_few_shot is None:
            use_few_shot = FEW_SHOT_CONFIG['enabled']
        
        # Check cache first
        cached_result = query_cache.get(question, schema)
        if cached_result:
            return cached_result
        
        # Optimize schema if enabled
        if PERFORMANCE_CONFIG['schema_optimization']:
            optimized_schema = optimize_schema_context(schema, question)
        else:
            optimized_schema = schema
        
        # Create prompt based on configuration
        if use_few_shot:
            examples = select_relevant_examples(question)
            prompt = create_few_shot_prompt(question, optimized_schema, examples)
            logger.info(f"Using few-shot prompting with {len(examples)} examples")
        else:
            prompt = create_standard_prompt(question, optimized_schema)
            logger.info("Using standard prompting")
        
        # Tokenize with proper handling
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=2048
        )
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        logger.info(f"Generating SQL for question: {question}")
        
        # Generate with optimized parameters
        with torch.no_grad():
            generated_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=MODEL_CONFIG['max_new_tokens'],
                temperature=MODEL_CONFIG['temperature'],
                top_p=MODEL_CONFIG['top_p'],
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                use_cache=MODEL_CONFIG.get('use_cache', True)
            )
        
        # Decode only the new tokens
        new_tokens = generated_ids[0][inputs["input_ids"].shape[1]:]
        generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        # Clean up the generated SQL
        sql_query = "SELECT" + generated_text.split("SELECT")[-1] if "SELECT" in generated_text else "SELECT " + generated_text
        
        # Validate SQL if enabled
        if PERFORMANCE_CONFIG['query_validation']:
            is_valid, validated_sql = validate_sql_syntax(sql_query)
            if not is_valid:
                logger.warning(f"Generated invalid SQL: {validated_sql}")
                error_sql = f"-- Error: {validated_sql}\n{sql_query}"
                query_cache.set(question, schema, error_sql)
                return error_sql
            sql_query = validated_sql
        
        # Cache the result
        query_cache.set(question, schema, sql_query)
        
        logger.info(f"Successfully generated SQL")
        return sql_query
        
    except Exception as e:
        logger.error(f"Error in SQL generation: {str(e)}")
        error_msg = f"-- Error generating SQL: {str(e)}"
        return error_msg

# Add the missing helper functions
def create_few_shot_prompt(question: str, schema: str, examples: list) -> str:
    """Create a prompt with few-shot examples"""
    prompt = f"{schema}\n\n"
    prompt += "-- Here are some example questions and their corresponding SQL queries:\n\n"
    
    for example in examples:
        prompt += f"-- Question: {example['question']}\n"
        prompt += f"{example['sql']}\n\n"
    
    prompt += f"-- Using valid MySQL, answer the following question for the tables provided above.\n"
    prompt += f"-- Question: {question}\n"
    prompt += "SELECT"
    
    return prompt

def create_standard_prompt(question: str, schema: str) -> str:
    """Create a standard prompt without examples"""
    prompt = f"""{schema}

-- Using valid MySQL, answer the following question for the tables provided above.
-- Question: {question}
SELECT"""
    return prompt

def get_cache_stats() -> dict:
    """Get cache statistics"""
    return {
        "cache_size": query_cache.size(),
        "max_size": query_cache.max_size,
        "cache_enabled": FEW_SHOT_CONFIG['cache_enabled']
    }

def clear_cache():
    """Clear the query cache"""
    query_cache.clear()


