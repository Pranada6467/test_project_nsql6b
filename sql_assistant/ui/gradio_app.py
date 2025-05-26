import gradio as gr
from models.sql_generator import generate_sql, get_cache_stats, clear_cache
from database.query_executor import execute_query
from utils.schema_extractor import get_database_schema
from utils.query_formatter import format_query_results
from utils.few_shot_examples import get_examples, add_custom_example
import logging

logger = logging.getLogger(__name__)

# Get schema once at startup
SCHEMA = get_database_schema()

def process_query(question, use_few_shot, show_examples):
    """Process a natural language query with options"""
    try:
        # Generate SQL query
        sql_query = generate_sql(question, SCHEMA, use_few_shot=use_few_shot)
        
        # Execute the query if it doesn't contain errors
        if not sql_query.startswith("-- Error"):
            results = execute_query(sql_query)
            formatted_results = format_query_results(results)
        else:
            formatted_results = "Query not executed due to errors."
        
        # Show examples if requested
        examples_text = ""
        if show_examples:
            examples = get_examples()
            examples_text = "Available Examples:\n\n"
            for i, example in enumerate(examples, 1):
                examples_text += f"{i}. Q: {example['question']}\n"
                examples_text += f"   SQL: {example['sql']}\n\n"
        
        return sql_query, formatted_results, examples_text
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return "", f"Error: {str(e)}", ""

def add_new_example(question, sql, keywords):
    """Add a new few-shot example"""
    try:
        keywords_list = [k.strip() for k in keywords.split(",")]
        success = add_custom_example(question, sql, keywords_list)
        if success:
            return "Example added successfully!"
        else:
            return "Failed to add example."
    except Exception as e:
        return f"Error adding example: {str(e)}"

def get_system_stats():
    """Get system statistics"""
    try:
        cache_stats = get_cache_stats()
        stats_text = f"""System Statistics:
Cache Size: {cache_stats['cache_size']}/{cache_stats['max_size']}
Cache Enabled: {cache_stats['cache_enabled']}
Available Examples: {len(get_examples())}
"""
        return stats_text
    except Exception as e:
        return f"Error getting stats: {str(e)}"

def clear_system_cache():
    """Clear the system cache"""
    try:
        clear_cache()
        return "Cache cleared successfully!"
    except Exception as e:
        return f"Error clearing cache: {str(e)}"

def create_gradio_interface():
    """Create and return enhanced Gradio interface"""
    with gr.Blocks(title="Advanced SQL Assistant") as interface:
        gr.Markdown("# Natural Language to SQL Assistant")
        gr.Markdown("Ask questions about your database in natural language with advanced features.")
        
        with gr.Tab("Query Generator"):
            with gr.Row():
                with gr.Column():
                    question_input = gr.Textbox(
                        lines=3,
                        placeholder="Ask a question about your database...",
                        label="Your Question"
                    )
                    
                    with gr.Row():
                        use_few_shot = gr.Checkbox(
                            value=True,
                            label="Use Few-Shot Prompting"
                        )
                        show_examples = gr.Checkbox(
                            value=False,
                            label="Show Available Examples"
                        )
                    
                    generate_btn = gr.Button("Generate SQL", variant="primary")
                
                with gr.Column():
                    sql_output = gr.Textbox(
                        label="Generated SQL Query",
                        lines=5
                    )
                    results_output = gr.Textbox(
                        label="Query Results",
                        lines=10
                    )
                    examples_output = gr.Textbox(
                        label="Available Examples",
                        lines=8
                    )
        
        with gr.Tab("Add Examples"):
            gr.Markdown("### Add New Few-Shot Examples")
            with gr.Row():
                with gr.Column():
                    new_question = gr.Textbox(
                        label="Question",
                        placeholder="What is the average salary?"
                    )
                    new_sql = gr.Textbox(
                        label="SQL Query",
                        placeholder="SELECT AVG(salary) FROM salaries;"
                    )
                    new_keywords = gr.Textbox(
                        label="Keywords (comma-separated)",
                        placeholder="average, salary, mean"
                    )
                    add_btn = gr.Button("Add Example")
                
                with gr.Column():
                    add_result = gr.Textbox(
                        label="Result",
                        lines=3
                    )
        
        with gr.Tab("System Info"):
            gr.Markdown("### System Statistics and Controls")
            with gr.Row():
                stats_btn = gr.Button("Get Statistics")
                clear_btn = gr.Button("Clear Cache")
            
            stats_output = gr.Textbox(
                label="System Statistics",
                lines=5
            )
            clear_result = gr.Textbox(
                label="Clear Result",
                lines=2
            )
        
        # Event handlers
        generate_btn.click(
            fn=process_query,
            inputs=[question_input, use_few_shot, show_examples],
            outputs=[sql_output, results_output, examples_output]
        )
        
        add_btn.click(
            fn=add_new_example,
            inputs=[new_question, new_sql, new_keywords],
            outputs=[add_result]
        )
        
        stats_btn.click(
            fn=get_system_stats,
            outputs=[stats_output]
        )
        
        clear_btn.click(
            fn=clear_system_cache,
            outputs=[clear_result]
        )
    
    return interface
