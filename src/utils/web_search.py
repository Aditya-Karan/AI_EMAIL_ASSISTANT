import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Your API key from Google Custom Search
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# Your custom search engine ID
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

def search_web(query):
    """
    Search the web using Google Custom Search API.
    
    :param query: The search query.
    :return: The snippet of the first search result or a fallback message.
    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url).json()
    
    if "items" in response:
        return response["items"][0]["snippet"]  # Return the snippet of the first result
    else:
        return "No results found."
