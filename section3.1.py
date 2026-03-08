import json
import re
import random

# Load sentiment scores
sentiment_dict = {}
with open("sentiment_scores.txt", "r", encoding="utf-8") as fin:
    for line in fin:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            word = parts[0].lower()
            score = int(parts[1])
            sentiment_dict[word] = score

# Function to calculate tweet sentiment
def calculate_sentiment(text):
    # Split text into words, removing punctuation
    words = re.split(r'[^a-zA-Z]+', text.lower())

    # Calculate total sentiment score
    total_score = 0
    for word in words:
        if word in sentiment_dict:
            total_score += sentiment_dict[word]

    return total_score

# Function to determine emotion based on score
def get_emotion(score):
    if score > 0:
        return "POSITIVE"
    elif score < 0:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

# Read tweets and calculate sentiments
tweets = []
with open("twitter_data1.txt", "r", encoding="utf-8") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet_data = json.loads(line)
                if "text" in tweet_data:
                    tweets.append(tweet_data)
            except:
                pass

# Select 10 random tweets
random_tweets = random.sample(tweets, min(10, len(tweets)))

# Display and save results
print("=" * 80)
print("TWEET SENTIMENT ANALYSIS")
print("=" * 80)
print()

for i, tweet in enumerate(random_tweets, 1):
    text = tweet["text"]
    sentiment_score = calculate_sentiment(text)
    emotion = get_emotion(sentiment_score)

    # Print to console with error handling for special characters
    try:
        print(f"Tweet {i}:")
        print(f"Text: {text}")
        print(f"Sentiment Score: {sentiment_score}")
        print(f"Emotion: {emotion}")
        print()
    except UnicodeEncodeError:
        # Fallback for characters that can't be displayed
        print(f"Tweet {i}:")
        print(f"Text: {text.encode('ascii', 'replace').decode('ascii')}")
        print(f"Sentiment Score: {sentiment_score}")
        print(f"Emotion: {emotion}")
        print()



