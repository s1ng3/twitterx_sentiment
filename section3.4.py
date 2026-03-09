import json
import re

# Load sentiment scores
sentiment_dict = {}
with open("sentiment_scores.txt", "r") as fin:
    for line in fin:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            word = parts[0].lower()
            score = int(parts[1])
            sentiment_dict[word] = score

# Calculate tweet sentiment
def calculate_sentiment(text):
    words = re.split(r'[^a-zA-Z]+', text.lower())
    total = 0
    for word in words:
        if word in sentiment_dict:
            total += sentiment_dict[word]
    return total

# Read tweets and collect user data
user_data = {}

with open("twitter_data1.txt", "r") as fin:
    for line in fin:
        line = line.strip()
        if line:
            try:
                tweet = json.loads(line)
                if "text" in tweet and "user" in tweet:
                    user_id = tweet["user"].get("id_str", "")
                    friends_count = tweet["user"].get("friends_count", 0)
                    sentiment = calculate_sentiment(tweet["text"])

                    if user_id not in user_data:
                        user_data[user_id] = {'friends': friends_count, 'sentiments': []}
                    user_data[user_id]['sentiments'].append(sentiment)
            except:
                pass

# Calculate average sentiment per user
user_list = []
for user_id, data in user_data.items():
    avg_sentiment = sum(data['sentiments']) / len(data['sentiments'])
    user_list.append({'friends': data['friends'], 'avg_sentiment': avg_sentiment})

# Split by median
friends_counts = [u['friends'] for u in user_list]
median = sorted(friends_counts)[len(friends_counts) // 2]

many_friends = [u for u in user_list if u['friends'] >= median]
few_friends = [u for u in user_list if u['friends'] < median]

# Calculate average sentiment for each group
avg_many = sum(u['avg_sentiment'] for u in many_friends) / len(many_friends)
avg_few = sum(u['avg_sentiment'] for u in few_friends) / len(few_friends)

# Display results
print(f"Number of users: {len(user_list)}")
print(f"The average number of friends: {median}")
print(f"Many friends (>={median}): {len(many_friends)} users, avg sentiment: {avg_many:.4f}")
print(f"Few friends (<{median}): {len(few_friends)} users, avg sentiment: {avg_few:.4f}")

if avg_many > avg_few:
    print(f"Many friends = more positive ({avg_many:.4f} > {avg_few:.4f})")
else:
    print(f"Many friends != more positive ({avg_many:.4f} vs {avg_few:.4f})")

