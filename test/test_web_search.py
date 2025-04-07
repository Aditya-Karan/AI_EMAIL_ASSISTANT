import sys
import os

# Set the absolute path to the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.web_search import search_web

# Test query
query = "Latest AI trends in 2025"

# Perform search
result = search_web(query)

# Print result
print(f"Search Result for '{query}':\n{result}")
