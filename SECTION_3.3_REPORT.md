# Section 3.3 - Sentiment Scores for New Words

## Solution Description

This script analyzes the top 500 most frequent words from the tweets collection and proposes sentiment scores for words that don't already exist in the sentiment dictionary (`sentiment_scores.txt`).

## Methodology

### Step 1: Classify Tweets
- Load existing sentiment dictionary (2,477 words)
- Calculate sentiment score for each tweet using existing dictionary
- Classify tweets as:
  - **Positive**: sentiment score > 0
  - **Negative**: sentiment score < 0  
  - **Neutral**: sentiment score = 0

### Step 2: Extract Top 500 Words
- Extract all words from tweets (excluding URL fragments, Twitter artifacts, single letters)
- Count word frequencies
- Get top 500 most frequent words

### Step 3: Analyze Word Distribution
For each word in top 500 that is NOT in the existing sentiment dictionary:
- Count appearances in positive tweets
- Count appearances in negative tweets
- Calculate positive ratio and negative ratio

### Step 4: Propose Sentiment Scores

**Thresholds Used:**
- "Many positive" = appears in ≥ 10% of positive tweets (≥ 274 appearances)
- "Many negative" = appears in ≥ 10% of negative tweets (≥ 159 appearances)

**Scoring Logic:**

1. **Strong Positive (+2)**: Appears in many positive tweets, few negative tweets, AND ≥80% positive ratio
2. **Mild Positive (+1)**: 
   - Appears in many positive tweets, few negative tweets, AND 65-80% positive ratio
   - OR appears in both many positive and many negative tweets with ≥65% positive ratio
   - OR not frequent enough but ≥70% positive ratio

3. **Strong Negative (-2)**: Appears in many negative tweets, few positive tweets, AND ≥80% negative ratio
4. **Mild Negative (-1)**:
   - Appears in many negative tweets, few positive tweets, AND 65-80% negative ratio
   - OR appears in both many positive and many negative tweets with ≥65% negative ratio
   - OR not frequent enough but ≥70% negative ratio

5. **Neutral (0)**: Everything else (mixed distribution, balanced between positive/negative)

## Results Summary

### Tweet Classification:
- Total tweets: **10,000**
- Positive tweets: **2,735** (27.4%)
- Negative tweets: **1,594** (15.9%)
- Neutral tweets: **5,671** (56.7%)

### Word Analysis:
- Top 500 words analyzed
- **430 words** need new sentiment scores
- **70 words** already in sentiment dictionary

### Key Findings:

**Examples of Proposed Positive Words:**
- **"you"** (+1): Appears in 67.3% positive, 32.7% negative tweets
- **"this"** (+1): Appears in 68.2% positive tweets
- **"for"** (+1): 66.1% positive, 33.9% negative
- **"from"** (+1): 71.3% positive
- **"new"** (+1): 72.4% positive
- **"kca"** (+1): 86.4% positive (Kids' Choice Awards hashtag)
- **"play"** (+1): 80.0% positive
- **"read"** (+1): 79.2% positive
- **"fans"** (+1): 80.8% positive

**Examples of Proposed Negative Words:**
- **"talking"** (-1): 71.4% negative
- (Most function words are neutral due to appearing in both categories)

**Examples of Neutral Words (0):**
- **"the"** (0): 64.1% positive, 35.9% negative - appears in both categories
- **"to"** (0): 64.2% positive, 35.8% negative
- **"in"**, **"is"**, **"of"**, **"it"**, **"on"** - all neutral function words
- **"people"** (0): 36.8% positive, 63.2% negative - but not frequent enough in either

## Handling Words Appearing in Both Categories

Words that appear in BOTH many positive AND many negative tweets are assigned based on:
- If ≥65% skew toward one category → assign mild sentiment (+1 or -1)
- If <65% skew → assign neutral (0)

This captures that common function words like "the", "to", "in" appear everywhere and shouldn't influence sentiment.

## Advantages of This Approach:

1. **Data-driven**: Based on actual usage in classified tweets
2. **Threshold-based**: Uses reasonable 10% threshold for "many"
3. **Ratio-aware**: Considers not just counts but proportions
4. **Handles mixed cases**: Special logic for words in both positive and negative tweets
5. **Conservative**: Only assigns non-zero scores when clear evidence exists

## Limitations:

1. Bootstrap problem: Initial classification depends on existing dictionary quality
2. Context-independent: Can't detect when same word has different meanings
3. Function words dominate: Most common words are neutral grammatical words
4. Threshold sensitivity: 10% threshold is somewhat arbitrary

## To Run:

```bash
python section3.3.py
```

Results are displayed in console showing:
- Word
- Proposed sentiment score (-2, -1, 0, +1, +2)
- Count in positive tweets
- Count in negative tweets
- Total frequency
- Reasoning for the proposed score

