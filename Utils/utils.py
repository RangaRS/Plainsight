def loadCSS(path):
    cssFile = open(path, "r")
    return f"""<style>{cssFile.read()}</style>"""


def calculate_sentiment_scores(data):
    """
    Calculate weighted sentiment scores from a pre-fetched dataset.

    This function assigns weights to entries based on their recency in the dataset 
    and calculates the percentage contribution of each sentiment category. 
    The dataset is expected to have a chronological order where earlier entries 
    are less recent, and later entries are more recent.

    Args:
        data (pandas.DataFrame): A DataFrame with at least two columns:
            - 'CREATED': A column representing the creation time or order of the data.
            - 'SENTIMENT': A column representing sentiment categories (e.g., positive, neutral, negative).

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - SENTIMENT: The sentiment category.
            - WEIGHT: The total weight for each sentiment category.
            - SCORE: The percentage contribution of each sentiment category to the overall weighted score.
    """
    # Ensure the data is sorted chronologically if not already
    data = data.sort_values(by='CREATED', ascending=False).reset_index(drop=True)

    # Assign weights based on recency
    data['WEIGHT'] = data.index[::-1] + 1

    # Calculate total weight score
    total_score = data['WEIGHT'].sum()

    # Group by sentiment and calculate weighted scores
    grouped_data = data.groupby('SENTIMENT', as_index=False)['WEIGHT'].sum()
    grouped_data['SCORE'] = (grouped_data['WEIGHT'] / total_score) * 100

    return grouped_data.sort_values(by='SCORE', ascending=False).reset_index()


def date_to_words(date_obj):
    """Convert a date object to words."""
    return date_obj.strftime("%A, %B %d, %Y")

def time_to_words(time_obj):
    """Convert a time object to words."""
    hour = time_obj.hour % 12
    if hour == 0:
        hour = 12
    meridiem = "AM" if time_obj.hour < 12 else "PM"
    return f"{hour}:{time_obj.strftime('%M')} {meridiem}"