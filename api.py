import requests
import nltk
import sqlite3
import json
import random
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data (run once)
# nltk.download("punkt_tab")
# nltk.download("stopwords")

# api_url = "https://jsonplaceholder.typicode.com/todos/1"

# response = requests.get(api_url)
# print(response.status_code)


# def extract_keywords(text):
#     stop_words = set(stopwords.words("english"))
#     words = word_tokenize(text.lower())  # Tokenize and convert to lowercase
#     keywords = [word for word in words if word.isalnum() and word not in stop_words]
#     return keywords


# question_text = "What is the capital of France?"
# keywords = extract_keywords(question_text)
# print(keywords)  # Output: ['capital', 'france']

import requests

def search_wikipedia(question):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": question,
        "format": "json"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get("query", {}).get("search", [])
        print(results)
        if results:
            return [
                f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"
                for result in results[:2]  # Get top 2 results
            ]
    return ["No relevant Wikipedia articles found."]

# Example usage
question_text = "What is the capital of France?"
links = search_wikipedia(question_text)
print(links)




