import json
import re

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
    words = re.split(r'[^a-zA-Z]+', text.lower())
    total_score = 0
    for word in words:
        if word in sentiment_dict:
            total_score += sentiment_dict[word]
    return total_score

# Read tweets and collect data: friends_count and sentiment
user_data = {}  # user_id -> {'friends': count, 'sentiments': [list of sentiment scores]}

print("Loading tweets and calculating sentiments...")
with open("twitter_data1.txt", "r", encoding="utf-8") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet = json.loads(line)
                if "text" in tweet and "user" in tweet:
                    user = tweet["user"]
                    user_id = user.get("id_str", "")
                    friends_count = user.get("friends_count", 0)
                    text = tweet["text"]

                    sentiment = calculate_sentiment(text)

                    # Store user data
                    if user_id not in user_data:
                        user_data[user_id] = {
                            'friends': friends_count,
                            'sentiments': []
                        }
                    user_data[user_id]['sentiments'].append(sentiment)
            except:
                pass

# Calculate average sentiment per user
user_analysis = []
for user_id, data in user_data.items():
    friends_count = data['friends']
    sentiments = data['sentiments']
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

    user_analysis.append({
        'user_id': user_id,
        'friends_count': friends_count,
        'avg_sentiment': avg_sentiment,
        'tweet_count': len(sentiments)
    })

print(f"Analyzed {len(user_analysis)} unique users")

# Define threshold for "many friends" vs "few friends"
# Use median as the split point
friends_counts = [u['friends_count'] for u in user_analysis]
median_friends = sorted(friends_counts)[len(friends_counts) // 2]

print(f"Median friends count: {median_friends}")

# Split users into two groups
many_friends = [u for u in user_analysis if u['friends_count'] >= median_friends]
few_friends = [u for u in user_analysis if u['friends_count'] < median_friends]

# Calculate average sentiment for each group
avg_sentiment_many = sum(u['avg_sentiment'] for u in many_friends) / len(many_friends) if many_friends else 0
avg_sentiment_few = sum(u['avg_sentiment'] for u in few_friends) / len(few_friends) if few_friends else 0

# Display results
print("\n" + "=" * 80)
print("HYPOTHESIS TEST: Do people with many friends post more positive tweets?")
print("=" * 80)
print(f"\nThreshold (median): {median_friends} friends")
print(f"\nGroup 1 - MANY FRIENDS (>= {median_friends} friends):")
print(f"  Users: {len(many_friends)}")
print(f"  Average sentiment: {avg_sentiment_many:.4f}")

print(f"\nGroup 2 - FEW FRIENDS (< {median_friends} friends):")
print(f"  Users: {len(few_friends)}")
print(f"  Average sentiment: {avg_sentiment_few:.4f}")

print(f"\nDifference: {avg_sentiment_many - avg_sentiment_few:.4f}")

# Determine conclusion
if avg_sentiment_many > avg_sentiment_few:
    print("\n✓ HYPOTHESIS SUPPORTED: People with many friends have more positive tweets")
    print(f"  ({avg_sentiment_many:.4f} vs {avg_sentiment_few:.4f})")
else:
    print("\n✗ HYPOTHESIS REJECTED: People with many friends do NOT have more positive tweets")
    print(f"  ({avg_sentiment_many:.4f} vs {avg_sentiment_few:.4f})")

# Additional analysis: Show distribution
print("\n" + "-" * 80)
print("Additional Analysis:")
print("-" * 80)

# Count positive, negative, neutral users in each group
many_positive = sum(1 for u in many_friends if u['avg_sentiment'] > 0)
many_negative = sum(1 for u in many_friends if u['avg_sentiment'] < 0)
many_neutral = sum(1 for u in many_friends if u['avg_sentiment'] == 0)

few_positive = sum(1 for u in few_friends if u['avg_sentiment'] > 0)
few_negative = sum(1 for u in few_friends if u['avg_sentiment'] < 0)
few_neutral = sum(1 for u in few_friends if u['avg_sentiment'] == 0)

print(f"\nMANY FRIENDS group:")
print(f"  Positive users: {many_positive} ({many_positive/len(many_friends)*100:.1f}%)")
print(f"  Negative users: {many_negative} ({many_negative/len(many_friends)*100:.1f}%)")
print(f"  Neutral users: {many_neutral} ({many_neutral/len(many_friends)*100:.1f}%)")

print(f"\nFEW FRIENDS group:")
print(f"  Positive users: {few_positive} ({few_positive/len(few_friends)*100:.1f}%)")
print(f"  Negative users: {few_negative} ({few_negative/len(few_friends)*100:.1f}%)")
print(f"  Neutral users: {few_neutral} ({few_neutral/len(few_friends)*100:.1f}%)")

print("\n" + "=" * 80)

