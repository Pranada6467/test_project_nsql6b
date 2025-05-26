# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'forget@7',
    'database': 'employees'
}

# Model configuration with optimizations
MODEL_CONFIG = {
    'model_name': 'NumbersStation/nsql-6B',
    'use_8bit': True,  # Enable 8-bit quantization for memory efficiency
    'device': 'auto',
    'max_new_tokens': 200,  # Limit new tokens instead of total length
    'temperature': 0.1,     # Lower temperature for more deterministic output
    'top_p': 0.9,          # Slightly lower top_p for better accuracy
    'use_cache': True,      # Enable KV cache for faster generation
}

# Few-shot prompting configuration
FEW_SHOT_CONFIG = {
    'enabled': True,
    'num_examples': 3,
    'use_semantic_similarity': False,  # Set to True if you install sentence-transformers
    'cache_enabled': True,
    'max_cache_size': 100
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    'schema_optimization': True,  # Enable smart schema filtering
    'query_validation': True,    # Enable SQL validation
    'logging_level': 'INFO'
}

