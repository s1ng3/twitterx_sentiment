import json
import re
from collections import Counter

# Load sentiment scores
sentiment_dict = {}
with open("sentiment_scores.txt", "r") as fin:
    for line in fin:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            word = parts[0].lower()
            score = int(parts[1])
            sentiment_dict[word] = score

# Words to exclude
EXCLUDE_WORDS = {
    't', 'co', 'https', 'http', 'rt', 'amp', 'www',
    's', 'm', 'n', 'o', 'u', 'e', 'y', 'd', 'x', 'k', 'l', 'r', 'b', 'c', 'g', 'p', 'f', 'w', 'h', 'v', 'j', 'q', 'z',
    'de', 'la', 'el', 'en', 'le', 'di', 'da', 'un', 'du', 'il', 'et'
}

# Calculate tweet sentiment
def calculate_sentiment(text):
    words = re.split(r'[^a-zA-Z]+', text.lower())
    total = 0
    for word in words:
        if word in sentiment_dict:
            total += sentiment_dict[word]
    return total

# Load tweets and classify them
positive_tweets = []
negative_tweets = []

with open("twitter_data1.txt", "r") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet_data = json.loads(line)
                if "text" in tweet_data:
                    text = tweet_data["text"]
                    sentiment = calculate_sentiment(text)

                    if sentiment > 0:
                        positive_tweets.append(text)
                    elif sentiment < 0:
                        negative_tweets.append(text)
            except:
                pass

# Get top 500 words
all_words = []
with open("twitter_data1.txt", "r") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet_data = json.loads(line)
                if "text" in tweet_data:
                    words = re.split(r'[^a-zA-Z]+', tweet_data["text"].lower())
                    words = [word for word in words if word and word not in EXCLUDE_WORDS and len(word) >= 2]
                    all_words.extend(words)
            except:
                pass

word_freq = Counter(all_words)
top_500 = word_freq.most_common(500)

# For each word in top 500, propose sentiment score
for word, freq in top_500:
    if word in sentiment_dict:
        continue

    # Count appearances in positive and negative tweets
    pos_count = 0
    neg_count = 0

    for tweet in positive_tweets:
        if word in re.split(r'[^a-zA-Z]+', tweet.lower()):
            pos_count += 1

    for tweet in negative_tweets:
        if word in re.split(r'[^a-zA-Z]+', tweet.lower()):
            neg_count += 1

    total = pos_count + neg_count

    if total == 0:
        proposed_score = 0
        ratio = 0.0
    else:
        ratio = pos_count / total

        # Sentiment score based on ratio thresholds
        if ratio >= 0.95:
            proposed_score = 5  # Very strong positive
        elif ratio >= 0.85:
            proposed_score = 4  # Strong positive
        elif ratio >= 0.75:
            proposed_score = 3  # Positive
        elif ratio >= 0.65:
            proposed_score = 2  # Mild positive
        elif ratio >= 0.55:
            proposed_score = 1  # Weak positive
        elif ratio > 0.45:
            proposed_score = 0  # Neutral
        elif ratio > 0.35:
            proposed_score = -1  # Weak negative
        elif ratio > 0.25:
            proposed_score = -2  # Mild negative
        elif ratio > 0.15:
            proposed_score = -3  # Negative
        elif ratio > 0.05:
            proposed_score = -4  # Strong negative
        else:
            proposed_score = -5  # Very strong negative

    print(f"{word}: score={proposed_score}, positive={pos_count}, negative={neg_count}, ratio={ratio:.2f}")