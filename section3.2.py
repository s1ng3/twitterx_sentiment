import json
import re
from collections import Counter

# Define words to exclude (URL fragments, Twitter artifacts, etc.)
EXCLUDE_WORDS = {
    't', 'co', 'https', 'http', 'rt', 'amp', 'www',
    's', 'm', 'n', 'o', 'u', 'e', 'y', 'd', 'x', 'k', 'l', 'r', 'b', 'c', 'g', 'p', 'f', 'w', 'h', 'v', 'j', 'q', 'z',  # single letters
    'de', 'la', 'el', 'en', 'le', 'di', 'da', 'un', 'du', 'il', 'et'  # common non-English articles
}

# Read tweets and extract all words
all_words = []

with open("twitter_data1.txt", "r") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet_data = json.loads(line)
                if "text" in tweet_data:
                    text = tweet_data["text"]
                    # Split text into words, removing punctuation
                    words = re.split(r'[^a-zA-Z]+', text.lower())
                    # Filter: remove empty strings, words in exclude list, and words shorter than 2 characters
                    words = [word for word in words if word and word not in EXCLUDE_WORDS and len(word) >= 2]
                    all_words.extend(words)
            except:
                pass

# Count word frequencies
word_freq = Counter(all_words)

# Get the 500 most common words
top_500 = word_freq.most_common(500)

for rank, (word, freq) in enumerate(top_500, 1):
    print(f"{rank} | {word} | {freq}")