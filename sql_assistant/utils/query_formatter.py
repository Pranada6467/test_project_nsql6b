def format_query_results(results):
    """Format query results for display"""
    if isinstance(results, list):
        if len(results) == 0:
            return "No results found."
        
        # Create header row
        headers = results[0].keys()
        formatted = " | ".join(headers) + "\n"
        formatted += "-" * len(formatted) + "\n"
        
        # Add data rows
        for row in results:
            formatted += " | ".join(str(value) for value in row.values()) + "\n"
        
        return formatted
    elif isinstance(results, dict) and "error" in results:
        return f"Error: {results['error']}"
    else:
        return str(results)
