import re
import pandas as pd

def preprocess(data):

    # Pattern for 12-hour format 
    pattern12 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s'

    # Pattern for 24-hour format
    pattern24 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    # Detect format
    if re.search(pattern12, data):
        pattern = pattern12
        date_format = '%d/%m/%y, %I:%M %p - '
    else:
        pattern = pattern24
        date_format = '%d/%m/%y, %H:%M - '

    # Split messages
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create dataframe
    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Convert date column
    df['message_date'] = pd.to_datetime(df['message_date'], format=date_format, errors='coerce')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:

        entry = re.split(r'([\w\W]+?):\s', message)

        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'], inplace=True)

    # -------- TIME FEATURES --------
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['date'] = df['date']
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Period for heatmap
    period = []

    for hour in df['hour']:
        start = pd.to_datetime(str(hour) + ":00").strftime("%I %p")
        end = pd.to_datetime(str((hour + 1) % 24) + ":00").strftime("%I %p")
        period.append(start + " - " + end)

    df['period'] = period

    return df
