import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

# Create nltk_data directory if it doesn't exist
nltk_data_dir = os.path.expanduser('~/nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Download required NLTK data silently
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def process_text_to_keywords(text):
    """
    Process text to extract keywords
    
    Args:
        text (str): Input text to process
        
    Returns:
        list: Extracted keywords
    """
    # Simple keyword extraction
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('spanish'))
    keywords = [word for word in tokens if word not in stop_words]
    return keywords 