# LangChain Cache Configuration

React Agent Generator now supports LangChain caching to improve performance and reduce API costs.

## Automatic Configuration

The React Agent Generator automatically configures caching when initialized:

```python
# In GeneratorConfig extra_params:
config = GeneratorConfig(
    name="react-agent",
    extra_params={
        "cache_path": "./my_cache.db"  # Optional, defaults to ".langchain.db"
    }
)
```

## Manual Configuration

You can also configure caching manually in your code:

```python
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

# Set up SQLite cache
set_llm_cache(SQLiteCache(database_path=".langchain.db"))
```

## Benefits

1. **Faster Response Times**: Cached responses are returned instantly
2. **Reduced API Costs**: Identical queries don't make new API calls
3. **Consistent Results**: Same inputs always produce same outputs
4. **Offline Development**: Work with cached responses when offline

## Cache Management

- Cache files are SQLite databases (`.db` files)
- Delete the cache file to clear all cached responses
- Cache is persistent across runs
- Different cache files can be used for different projects

## Example Usage

```python
# First call - hits the API
result1 = generator.generate_psm(pim_content)  # Takes ~2 minutes

# Second call - uses cache
result2 = generator.generate_psm(pim_content)  # Takes <1 second
```

## Notes

- Cache is based on exact input matching
- Includes system prompts, user messages, and model parameters
- Works with all LangChain LLM calls in the React Agent