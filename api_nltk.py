import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# use the nltk app to get keywords from the questions to feed to Wikipedia API
def extract_keywords(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    keywords = [word for word in words if word.isalnum() and word not in stop_words]
    return keywords

# Download required NLTK data (run once)
nltk.download("punkt_tab")
nltk.download("stopwords")
