from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import yfinance as yf


class LoadData:
    """
    A class to load financial and news data for a given stock symbol.

    This includes:
    - Historical stock data using Yahoo Finance.
    - News articles from NewsAPI and APITube.
    """

    def __init__(self, stock_symbol: str):
        """
        Initializes the LoadData class with a stock ticker symbol.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., 'AAPL').
        """
        self.stock_symbol = stock_symbol
        self.start_date = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")
        self.api_keys = self._load_api_keys()
        ticker = yf.Ticker(stock_symbol)
        self.name = ticker.info.get("displayName", stock_symbol)

    def _load_api_keys(self) -> tuple[str, str]:
        """
        Loads NewsAPI and APITube API keys from a .env file.

        Returns:
            tuple: (news_api_key, apitube_api_key)

        Raises:
            ValueError: If any API key is missing from the environment.
        """
        load_dotenv()
        api_key_news = os.getenv("API_KEY_NEWSAPI")
        api_key_apitube = os.getenv("API_KEY_APITUBE")

        missing = []
        if not api_key_news:
            missing.append("NewsAPI")
        if not api_key_apitube:
            missing.append("APITube")

        if missing:
            raise ValueError(
                f"Missing API key(s): {', '.join(missing)}. Check your .env file."
            )

        return api_key_news, api_key_apitube

    def load_stock_data(
        self, start_date: datetime | None = None
    ) -> pd.DataFrame | None:
        """
        Downloads historical stock data using yfinance.

        Args:
            start_date (datetime | None): Optional start date. If not provided, defaults to
                12 weeks ago from today.

        Returns:
            pd.DataFrame | None: DataFrame with Open, High, Low, Close, and Volume columns,
                or None if no data is found.
        """
        start_date_str = (
            start_date.strftime("%Y-%m-%d") if start_date else self.start_date
        )

        stock_data = yf.download(self.stock_symbol, start=start_date_str)

        if stock_data.empty:
            print(f"No data found for '{self.stock_symbol}'.")
            return None

        return stock_data[["Open", "High", "Low", "Close", "Volume"]]

    def load_news_data(self) -> pd.DataFrame:
        """
        Fetches recent news articles using NewsAPI, day-by-day from start_date.

        Returns:
            pd.DataFrame: DataFrame containing article headline, publication date, and description.
        """
        api_key = self.api_keys[0]
        all_articles = []
        date = datetime.strptime(self.start_date, "%Y-%m-%d")
        today = datetime.now()

        while date <= today:
            date_str = date.strftime("%Y-%m-%d")
            url = (
                f"https://newsapi.org/v2/everything?q={self.name}"
                f"&from={date_str}&to={date_str}&sortBy=popularity&apiKey={api_key}"
            )
            response = requests.get(url, timeout=10)
            data = response.json()
            date += timedelta(days=1)

            if "articles" in data:
                if not data["articles"]:
                    continue
                all_articles.extend(data["articles"])
            else:
                break

        headlines = [
            (article["title"], article["publishedAt"], article["description"])
            for article in all_articles
        ]
        return pd.DataFrame(headlines, columns=["headline", "date", "description"])

    def load_apitube_data(self) -> pd.DataFrame:
        """
        Fetches news articles related to the stock using the APITube API.

        Returns:
            pd.DataFrame: DataFrame containing article headline, publication date, and description.
        """
        api_key = self.api_keys[1]
        url = "https://api.apitube.io/v1/news/top-headlines"
        query_params = {
            "title": self.name,
            "api_key": api_key,
            "per_page": 500,
            "published_at.start": "2022-01-01",
            "published_at.end": "NOW",
            "is_duplicate": "true",
            "sort_by": "published_at",
        }

        response = requests.get(url, params=query_params, timeout=10)
        data = response.json()

        if "results" not in data:
            print("No results found in APITube response.")
            return pd.DataFrame()

        records = [
            {
                "date": item["published_at"],
                "headline": item["title"],
                "description": item["description"],
            }
            for item in data["results"]
        ]

        df = pd.DataFrame(records).drop_duplicates(subset=["headline"])
        return df
