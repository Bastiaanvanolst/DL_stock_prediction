from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import pandas as pd


class Sentiment:
    """
    A class for analyzing sentiment using two models:
    - VADER for general-purpose sentiment scoring.
    - FinBERT for financial text sentiment classification.
    """

    def __init__(self):
        """
        Initializes the sentiment analyzers.
        """
        self.vader = SentimentIntensityAnalyzer()
        self.finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")

    def _get_vader_sentiment(self, text: str) -> float:
        """
        Computes compound VADER sentiment score for a given text.

        Args:
            text (str): The text to analyze.

        Returns:
            float: Compound sentiment score in range [-1, 1].
        """
        if not isinstance(text, str) or not text.strip():
            return 0.0
        sentiment = self.vader.polarity_scores(text)
        return sentiment["compound"]

    def add_vader_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a VADER sentiment score column to the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing a 'headline' column.

        Returns:
            pd.DataFrame: DataFrame with added 'sentiment' column.
        """
        if "headline" not in df.columns:
            raise ValueError("Missing 'headline' column in input DataFrame.")

        df["sentiment"] = df["headline"].apply(self._get_vader_sentiment)
        return df

    def _get_finbert_sentiment(self, text: str) -> int:
        """
        Classifies sentiment using FinBERT.

        Args:
            text (str): Financial news description.

        Returns:
            int: Sentiment class (1=positive, -1=negative, 0=neutral).
        """
        if not isinstance(text, str) or not text.strip():
            return 0

        result = self.finbert(text)[0]
        label = result["label"].lower()
        return {"positive": 1, "negative": -1}.get(label, 0)

    def add_finbert_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a FinBERT sentiment score column to the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing a 'description' column.

        Returns:
            pd.DataFrame: DataFrame with added 'finbert_sentiment' column.
        """
        if "description" not in df.columns:
            raise ValueError("Missing 'description' column in input DataFrame.")

        df["finbert_sentiment"] = df["description"].apply(self._get_finbert_sentiment)
        return df
