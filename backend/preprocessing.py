
import pandas as pd


def preprocess_matches(matches):
    """
    Clean and prepare IPL match data.
    """

    matches = matches.copy()

    # Convert date column
    if "date" in matches.columns:
        matches["date"] = pd.to_datetime(
            matches["date"],
            errors="coerce"
        )

    # Remove duplicate matches
    if "match_id" in matches.columns:
        matches = matches.drop_duplicates(
            subset=["match_id"]
        )

    # Handle missing values
    for column in ["city", "venue"]:
        if column in matches.columns:
            matches[column] = matches[column].fillna("Unknown")

    # Convert season to numeric
    if "season" in matches.columns:
        matches["season"] = pd.to_numeric(
            matches["season"],
            errors="coerce"
        )

    return matches


def preprocess_deliveries(deliveries):
    """
    Clean and prepare ball-by-ball IPL data.
    """

    deliveries = deliveries.copy()

    # Remove duplicate records
    deliveries = deliveries.drop_duplicates()

    # Handle missing player names
    for column in ["batsman", "bowler", "batting_team"]:
        if column in deliveries.columns:
            deliveries[column] = deliveries[column].fillna("Unknown")

    # Convert numeric columns
    numeric_columns = [
        "batsman_runs",
        "total_runs",
        "bowler_runs",
        "legal_ball",
        "batter_ball",
        "is_wicket"
    ]

    for column in numeric_columns:
        if column in deliveries.columns:
            deliveries[column] = pd.to_numeric(
                deliveries[column],
                errors="coerce"
            ).fillna(0)

    return deliveries


def get_cleaning_summary(original, cleaned):
    """
    Display how many records were removed during cleaning.
    """

    original_count = len(original)
    cleaned_count = len(cleaned)

    return {
        "Original Records": original_count,
        "Cleaned Records": cleaned_count,
        "Removed Records": original_count - cleaned_count
    }
