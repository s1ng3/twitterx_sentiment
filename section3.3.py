import json
import re
from collections import Counter

# Load existing sentiment scores
sentiment_dict = {}
with open("sentiment_scores.txt", "r", encoding="utf-8") as fin:
    for line in fin:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            word = parts[0].lower()
            score = int(parts[1])
            sentiment_dict[word] = score

print(f"Loaded {len(sentiment_dict)} existing sentiment words")

# Define words to exclude (URL fragments, Twitter artifacts, etc.)
EXCLUDE_WORDS = {
    't', 'co', 'https', 'http', 'rt', 'amp', 'www',
    's', 'm', 'n', 'o', 'u', 'e', 'y', 'd', 'x', 'k', 'l', 'r', 'b', 'c', 'g', 'p', 'f', 'w', 'h', 'v', 'j', 'q', 'z',
    'de', 'la', 'el', 'en', 'le', 'di', 'da', 'un', 'du', 'il', 'et'
}

# Function to calculate tweet sentiment (for classification)
def calculate_tweet_sentiment(text):
    words = re.split(r'[^a-zA-Z]+', text.lower())
    total_score = 0
    for word in words:
        if word in sentiment_dict:
            total_score += sentiment_dict[word]
    return total_score

# Read all tweets and classify them
tweets = []
positive_tweets = []
negative_tweets = []
neutral_tweets = []

print("Loading and classifying tweets...")
with open("twitter_data1.txt", "r", encoding="utf-8") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet_data = json.loads(line)
                if "text" in tweet_data:
                    text = tweet_data["text"]
                    sentiment = calculate_tweet_sentiment(text)

                    tweets.append({"text": text, "sentiment": sentiment})

                    if sentiment > 0:
                        positive_tweets.append(text)
                    elif sentiment < 0:
                        negative_tweets.append(text)
                    else:
                        neutral_tweets.append(text)
            except:
                pass

print(f"Total tweets: {len(tweets)}")
print(f"Positive tweets: {len(positive_tweets)}")
print(f"Negative tweets: {len(negative_tweets)}")
print(f"Neutral tweets: {len(neutral_tweets)}")

# Extract all words and get top 500
all_words = []
for tweet in tweets:
    words = re.split(r'[^a-zA-Z]+', tweet["text"].lower())
    words = [word for word in words if word and word not in EXCLUDE_WORDS and len(word) >= 2]
    all_words.extend(words)

word_freq = Counter(all_words)
top_500 = word_freq.most_common(500)

print(f"\nAnalyzing top 500 most frequent words...")

# For each word in top 500, count appearances in positive/negative tweets
word_sentiment_stats = {}

for word, freq in top_500:
    # Skip if word already has a sentiment score
    if word in sentiment_dict:
        continue

    pos_count = 0
    neg_count = 0

    # Count appearances in positive and negative tweets
    for tweet_text in positive_tweets:
        words_in_tweet = re.split(r'[^a-zA-Z]+', tweet_text.lower())
        if word in words_in_tweet:
            pos_count += 1

    for tweet_text in negative_tweets:
        words_in_tweet = re.split(r'[^a-zA-Z]+', tweet_text.lower())
        if word in words_in_tweet:
            neg_count += 1

    word_sentiment_stats[word] = {
        'positive_count': pos_count,
        'negative_count': neg_count,
        'total_count': freq
    }

# Propose sentiment scores based on positive/negative appearances
# Thresholds:
# - "many" = appears in at least 10% of positive/negative tweets
# - Consider ratio of positive to negative appearances
proposed_sentiments = []

pos_threshold = len(positive_tweets) * 0.10  # 10% of positive tweets
neg_threshold = len(negative_tweets) * 0.10  # 10% of negative tweets

for word, stats in word_sentiment_stats.items():
    pos_count = stats['positive_count']
    neg_count = stats['negative_count']
    total = pos_count + neg_count

    if total == 0:
        # Word doesn't appear in classified tweets
        proposed_score = 0
        reason = "No appearances in classified tweets"
    else:
        # Calculate ratio
        pos_ratio = pos_count / total if total > 0 else 0
        neg_ratio = neg_count / total if total > 0 else 0

        # Determine sentiment score based on ratios and thresholds
        if pos_count >= pos_threshold and neg_count < neg_threshold:
            # Appears in many positive tweets, few negative tweets
            if pos_ratio >= 0.8:
                proposed_score = 2  # Strong positive
                reason = f"Appears in {pos_ratio:.1%} positive tweets"
            elif pos_ratio >= 0.65:
                proposed_score = 1  # Mild positive
                reason = f"Appears in {pos_ratio:.1%} positive tweets"
            else:
                proposed_score = 0
                reason = f"Mixed distribution ({pos_ratio:.1%} positive)"
        elif neg_count >= neg_threshold and pos_count < pos_threshold:
            # Appears in many negative tweets, few positive tweets
            if neg_ratio >= 0.8:
                proposed_score = -2  # Strong negative
                reason = f"Appears in {neg_ratio:.1%} negative tweets"
            elif neg_ratio >= 0.65:
                proposed_score = -1  # Mild negative
                reason = f"Appears in {neg_ratio:.1%} negative tweets"
            else:
                proposed_score = 0
                reason = f"Mixed distribution ({neg_ratio:.1%} negative)"
        elif pos_count >= pos_threshold and neg_count >= neg_threshold:
            # Appears in both many positive and many negative tweets
            if pos_ratio >= 0.65:
                proposed_score = 1
                reason = f"Mixed but leans positive ({pos_ratio:.1%} pos, {neg_ratio:.1%} neg)"
            elif neg_ratio >= 0.65:
                proposed_score = -1
                reason = f"Mixed but leans negative ({pos_ratio:.1%} pos, {neg_ratio:.1%} neg)"
            else:
                proposed_score = 0
                reason = f"Appears in both positive and negative ({pos_ratio:.1%} pos, {neg_ratio:.1%} neg)"
        else:
            # Not frequent enough in either category
            if pos_ratio >= 0.70:
                proposed_score = 1
                reason = f"Leans positive ({pos_ratio:.1%} positive)"
            elif neg_ratio >= 0.70:
                proposed_score = -1
                reason = f"Leans negative ({neg_ratio:.1%} negative)"
            else:
                proposed_score = 0
                reason = f"Neutral/mixed distribution ({pos_ratio:.1%} pos, {neg_ratio:.1%} neg)"

    proposed_sentiments.append({
        'word': word,
        'score': proposed_score,
        'pos_count': pos_count,
        'neg_count': neg_count,
        'total_freq': stats['total_count'],
        'reason': reason
    })

# Sort by total frequency (descending)
proposed_sentiments.sort(key=lambda x: x['total_freq'], reverse=True)

# Display results
print("\n" + "=" * 100)
print("PROPOSED SENTIMENT SCORES FOR NEW WORDS")
print("=" * 100)
print(f"\nWords from top 500 that need sentiment scores: {len(proposed_sentiments)}")
print(f"Words already in sentiment dictionary: {500 - len(proposed_sentiments)}")
print("\nThresholds used:")
print(f"  - 'Many positive': >= {pos_threshold:.0f} appearances in positive tweets ({len(positive_tweets)} total positive)")
print(f"  - 'Many negative': >= {neg_threshold:.0f} appearances in negative tweets ({len(negative_tweets)} total negative)")
print("\n" + "-" * 100)
print(f"{'Word':<15} | {'Score':>5} | {'Pos':>5} | {'Neg':>5} | {'Freq':>6} | {'Reason':<50}")
print("-" * 100)

for item in proposed_sentiments:
    try:
        print(f"{item['word']:<15} | {item['score']:>5} | {item['pos_count']:>5} | {item['neg_count']:>5} | {item['total_freq']:>6} | {item['reason']:<50}")
    except UnicodeEncodeError:
        word_safe = item['word'].encode('ascii', 'ignore').decode('ascii')
        print(f"{word_safe:<15} | {item['score']:>5} | {item['pos_count']:>5} | {item['neg_count']:>5} | {item['total_freq']:>6} | {item['reason']:<50}")

print("=" * 100)

# Summary statistics
positive_proposed = sum(1 for item in proposed_sentiments if item['score'] > 0)
negative_proposed = sum(1 for item in proposed_sentiments if item['score'] < 0)
neutral_proposed = sum(1 for item in proposed_sentiments if item['score'] == 0)

print(f"\nSummary:")
print(f"  Positive sentiment proposed: {positive_proposed}")
print(f"  Negative sentiment proposed: {negative_proposed}")
print(f"  Neutral sentiment proposed: {neutral_proposed}")
print(f"  Total: {len(proposed_sentiments)}")

