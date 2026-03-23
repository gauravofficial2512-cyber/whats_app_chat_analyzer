import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import seaborn as sns
import preprocessor
import helper

# PAGE CONFIG
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stButton>button {
    background-color: #25D366;
    color: white;
    border-radius: 10px;
    padding: 8px 20px;
    border: none;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #1ebe5d;
    color: white;
}

/* FEATURE BLOCKS */

.feature-container {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 20px;
    margin-top: 20px;
}

.feature-card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: 0.3s;
    border: 1px solid rgba(255,255,255,0.1);
}

.feature-card:hover{
    transform: translateY(-5px);
    background: rgba(255,255,255,0.1);
}

.feature-title{
    font-size:18px;
    font-weight:bold;
}

.feature-desc{
    font-size:14px;
    opacity:0.8;
}

</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("💬 WhatsApp Chat Analyzer")
st.sidebar.markdown("Upload your exported WhatsApp chat file.")

# TITLE
st.title("📊 WhatsApp Chat Analyzer Dashboard")
st.markdown("Analyze your WhatsApp conversations with beautiful insights.")

# FEATURE BLOCKS (FRONT PAGE INFO)
st.markdown("""
<div class="feature-container">

<div class="feature-card">
<div class="feature-title">📊 Overview</div>
<div class="feature-desc">
Shows total messages, words, media files and links shared in the chat.
</div>
</div>

<div class="feature-card">
<div class="feature-title">📅 Timeline</div>
<div class="feature-desc">
Visualize monthly and daily chat activity to understand conversation trends.
</div>
</div>

<div class="feature-card">
<div class="feature-title">🔥 Activity</div>
<div class="feature-desc">
Find the busiest days, months and active hours using heatmaps.
</div>
</div>

<div class="feature-card">
<div class="feature-title">☁ Word Analysis</div>
<div class="feature-desc">
Generate word clouds and discover the most frequently used words.
</div>
</div>

<div class="feature-card">
<div class="feature-title">😀 Emoji Insights</div>
<div class="feature-desc">
Identify the most used emojis and visualize them in a pie chart.
</div>
</div>

<div class="feature-card">
<div class="feature-title">👥 Busy Users</div>
<div class="feature-desc">
Discover which participants send the most messages in group chats.
</div>
</div>

<div class="feature-card">
<div class="feature-title">📈 Trends</div>
<div class="feature-desc">
Analyze long-term chat patterns and conversation spikes.
</div>
</div>

<div class="feature-card">
<div class="feature-title">⚡ Instant Insights</div>
<div class="feature-desc">
Upload your exported WhatsApp chat and get analytics instantly.
</div>
</div>

</div>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Upload Chat File")

if uploaded_file is not None:

    st.success("Chat file uploaded successfully ✅")

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data)

    if df.empty:
        st.warning("No messages found in file.")
        st.stop()

    users = df['user'].unique().tolist()

    if 'group_notification' in users:
        users.remove('group_notification')

    if len(users) == 2:
        st.subheader(f"Chat between **{users[0]}** and **{users[1]}**")
    else:
        st.subheader("Group Conversation Analysis")

    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Select User", user_list)

    if st.sidebar.button("Analyze Chat"):

        with st.spinner("Analyzing chat..."):

            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "📅 Timeline",
            "🔥 Activity",
            "☁ Word Analysis",
            "😀 Emojis"
        ])

        # OVERVIEW
        with tab1:

            st.subheader("Top Statistics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Messages", num_messages)
            col2.metric("Words", words)
            col3.metric("Media", num_media_messages)
            col4.metric("Links", num_links)

            if selected_user == 'Overall':

                st.subheader("Most Busy Users")

                x, new_df = helper.most_busy_users(df)

                col1, col2 = st.columns(2)

                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

        # TIMELINE
        with tab2:

            st.subheader("Monthly Timeline")

            timeline = helper.monthly_timeline(selected_user, df)

            if not timeline.empty:

                fig = px.line(
                    timeline,
                    x='time',
                    y='message',
                    markers=True
                )

                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Daily Timeline")

            daily_timeline = helper.daily_timeline(selected_user, df)

            if not daily_timeline.empty:

                fig = px.line(
                    daily_timeline,
                    x='date',
                    y='message'
                )

                st.plotly_chart(fig, use_container_width=True)

        # ACTIVITY
        with tab3:

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Most Busy Day")

                busy_day = helper.week_activity_map(selected_user, df)

                if not busy_day.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values)
                    st.pyplot(fig)

            with col2:

                st.subheader("Most Busy Month")

                busy_month = helper.month_activity_map(selected_user, df)

                if not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values)
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

            st.subheader("Weekly Heatmap")

            user_heatmap = helper.activity_heatmap(selected_user, df)

            if not user_heatmap.empty:

                fig, ax = plt.subplots(figsize=(12,5))
                sns.heatmap(user_heatmap, ax=ax)

                st.pyplot(fig)

        # WORD ANALYSIS
        with tab4:

            st.subheader("Word Cloud")

            df_wc = helper.create_wordcloud(selected_user, df)

            if df_wc is not None:

                fig, ax = plt.subplots()

                ax.imshow(df_wc)
                ax.axis("off")

                st.pyplot(fig)

            st.subheader("Most Common Words")

            most_common_df = helper.most_common_words(selected_user, df)

            if not most_common_df.empty:

                fig, ax = plt.subplots()

                ax.barh(most_common_df[0], most_common_df[1])

                st.pyplot(fig)

        # EMOJI ANALYSIS
        with tab5:

            st.subheader("Emoji Analysis")

            emoji_df = helper.emoji_helper(selected_user, df)

            if not emoji_df.empty:

                emoji_df = emoji_df.rename(columns={0: 'emoji', 1: 'count'})
                emoji_df.index = emoji_df.index + 1

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(emoji_df)

                with col2:

                    fig = px.pie(
                        emoji_df.head(10),
                        names='emoji',
                        values='count'
                    )

                    st.plotly_chart(fig)

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")


