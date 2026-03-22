import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import seaborn as sns
import preprocessor
import helper

st.sidebar.title("Whatsapp Chat Analyzer")
st.title("Welcome to WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data)

    if df.empty:
        st.write("No messages found in file.")
        st.stop()

    # Detect chat participants
    users = df['user'].unique().tolist()

    if 'group_notification' in users:
        users.remove('group_notification')

    # Display chat type
    if len(users) == 2:
        st.header(f"Chat Analysis Statistics between {users[0]} and {users[1]}")
    else:
        st.header("Group Conversation Analysis")

    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Total Media Shared", num_media_messages)
        col4.metric("Total Links Shared", num_links)

        # MONTHLY TIMELINE
        st.title("Monthly Timeline")

        timeline = helper.monthly_timeline(selected_user, df)

        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'])
            plt.xticks(rotation=90)
            st.pyplot(fig)
        else:
            st.write("No data available")

        # DAILY TIMELINE
        st.title("Daily Timeline")

        daily_timeline = helper.daily_timeline(selected_user, df)

        if not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['date'], daily_timeline['message'])
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("No data available")

        # ACTIVITY MAP
        st.title('Activity Map')

        col1, col2 = st.columns(2)

        with col1:
            st.header('Most Busy Day')
            busy_day = helper.week_activity_map(selected_user, df)

            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                st.pyplot(fig)
            else:
                st.write("No data available")

        with col2:
            st.header('Most Busy Month')
            busy_month = helper.month_activity_map(selected_user, df)

            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values)
                plt.xticks(rotation=90)
                st.pyplot(fig)
            else:
                st.write("No data available")

        # WEEKLY HEATMAP
        st.title("Weekly Activity Map")

        user_heatmap = helper.activity_heatmap(selected_user, df)

        if not user_heatmap.empty:
            fig, ax = plt.subplots(figsize=(12,5))
            sns.heatmap(user_heatmap, ax=ax)
            st.pyplot(fig)
        else:
            st.write("No activity data available for heatmap")

        # BUSIEST USERS
        if selected_user == 'Overall':

            st.title("Most Busy Users")

            x, new_df = helper.most_busy_users(df)

            if not x.empty:

                col1, col2 = st.columns(2)

                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation=90)
                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

            else:
                st.write("No user data available")

        # WORDCLOUD
        st.title("WordCloud")

        df_wc = helper.create_wordcloud(selected_user, df)

        if df_wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("No words available to generate wordcloud")

        # MOST COMMON WORDS
        st.title("Most Common Words")

        most_common_df = helper.most_common_words(selected_user, df)

        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            st.pyplot(fig)
        else:
            st.write("No common words found")

        # EMOJI ANALYSIS
        st.title("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:

            emoji_df = emoji_df.rename(columns={0: 'emoji', 1: 'count'})
            emoji_df.index = emoji_df.index + 1
            emoji_df.index.name = "No."

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:
                top_emoji_df = emoji_df.head(10)

                fig = px.pie(
                    top_emoji_df,
                    names='emoji',
                    values='count'
                )

                st.plotly_chart(fig)

        else:
            st.write("No emojis found")
