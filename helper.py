from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()


# ---------------- FETCH STATS ----------------
def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []
    for message in df['message'].astype(str):
        words.extend(message.split())

    num_media_messages = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

    links = []
    for message in df['message'].astype(str):
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# ---------------- MOST BUSY USERS ----------------
def most_busy_users(df):

    df = df[df['user'] != 'group_notification']

    x = df['user'].value_counts().head()

    new_df = round(
        (df['user'].value_counts() / df.shape[0]) * 100, 2
    ).reset_index()

    new_df.columns = ['name', 'percent']

    return x, new_df


# ---------------- WORDCLOUD ----------------
def create_wordcloud(selected_user, df):

    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = f.read().split()
    except:
        stop_words = []

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    words = []

    for message in temp['message'].astype(str):
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    if len(words) == 0:
        return None

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white'
    )

    text = " ".join(words)

    return wc.generate(text)


# ---------------- MOST COMMON WORDS ----------------
def most_common_words(selected_user, df):

    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = f.read().split()
    except:
        stop_words = []

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    words = []

    for message in temp['message'].astype(str):
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    if len(words) == 0:
        return pd.DataFrame()

    most_common_df = pd.DataFrame(Counter(words).most_common(20))

    return most_common_df


# ---------------- EMOJI ANALYSIS ----------------
def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message'].astype(str):
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    if len(emojis) == 0:
        return pd.DataFrame()

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


# ---------------- MONTHLY TIMELINE ----------------
def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


# ---------------- DAILY TIMELINE ----------------
def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily = df.groupby('date').count()['message'].reset_index()

    return daily


# ---------------- WEEK ACTIVITY ----------------
def week_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


# ---------------- MONTH ACTIVITY ----------------
def month_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


# ---------------- HEATMAP ----------------
def activity_heatmap(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()

    heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return heatmap
