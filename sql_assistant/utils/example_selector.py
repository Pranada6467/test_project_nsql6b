import logging
from typing import List, Dict
from utils.few_shot_examples import get_examples
from config.config import FEW_SHOT_CONFIG

logger = logging.getLogger(__name__)

def select_examples_by_keywords(question: str, num_examples: int = None) -> List[Dict]:
    """Select most relevant examples based on keyword matching"""
    if num_examples is None:
        num_examples = FEW_SHOT_CONFIG['num_examples']
    
    examples = get_examples()
    question_lower = question.lower()
    scored_examples = []
    
    for example in examples:
        score = 0
        
        # Score based on keyword matches
        for keyword in example.get('keywords', []):
            if keyword.lower() in question_lower:
                score += 2  # Higher weight for exact keyword matches
        
        # Score based on common words in questions
        question_words = set(question_lower.split())
        example_words = set(example["question"].lower().split())
        common_words = question_words.intersection(example_words)
        score += len(common_words)
        
        scored_examples.append((score, example))
    
    # Sort by score and return top examples
    scored_examples.sort(key=lambda x: x[0], reverse=True)
    selected = [example for _, example in scored_examples[:num_examples]]
    
    logger.info(f"Selected {len(selected)} examples for question: {question}")
    return selected

# Optional: Semantic similarity selection (requires sentence-transformers)
def select_examples_by_similarity(question: str, num_examples: int = None) -> List[Dict]:
    """Select examples using semantic similarity (requires sentence-transformers)"""
    try:
        from sentence_transformers import SentenceTransformer
        
        if num_examples is None:
            num_examples = FEW_SHOT_CONFIG['num_examples']
        
        # Load a lightweight sentence transformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        examples = get_examples()
        
        question_embedding = model.encode([question])
        example_embeddings = model.encode([ex["question"] for ex in examples])
        
        # Calculate cosine similarity
        similarities = model.similarity(question_embedding, example_embeddings)[0]
        
        # Get top similar examples
        top_indices = similarities.argsort(descending=True)[:num_examples]
        selected = [examples[i] for i in top_indices]
        
        logger.info(f"Selected {len(selected)} examples using semantic similarity")
        return selected
        
    except ImportError:
        logger.warning("sentence-transformers not installed, falling back to keyword matching")
        return select_examples_by_keywords(question, num_examples)

def select_relevant_examples(question: str, num_examples: int = None) -> List[Dict]:
    """Main function to select examples based on configuration"""
    if FEW_SHOT_CONFIG['use_semantic_similarity']:
        return select_examples_by_similarity(question, num_examples)
    else:
        return select_examples_by_keywords(question, num_examples)
