from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import yfinance as yf


class LoadData:
    def __init__(self, stock_symbol):
        """
        Initializes the LoadData class with a stock symbol.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., 'AAPL').
        """
        self.stock_symbol = stock_symbol
        self.start_date = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")
        self.api_keys = self.load_api_keys()
        ticker = yf.Ticker(self.stock_symbol)
        self.name = ticker.info["displayName"]

    def load_api_keys(self):
        """
        Loads API keys from the .env file.

        Returns:
            tuple: API keys for NewsAPI and APITube.
        Raises:
            ValueError: If any of the required API keys are not found.
        """
        load_dotenv()

        api_key_news = os.getenv("API_KEY_NEWSAPI")
        api_key_apitube = os.getenv("API_KEY_APITUBE")

        if not api_key_news or not api_key_apitube:
            missing_keys = []
            if not api_key_news:
                missing_keys.append("NewsAPI")
            if not api_key_apitube:
                missing_keys.append("APITube")
            raise ValueError(
                f"API Key(s) not found for: {', '.join(missing_keys)}. Check your .env file."
            )

        return api_key_news, api_key_apitube

    def load_stock_data(self):
        """
        Downloads historical stock data for the initialized stock symbol.

        Returns:
            pandas.DataFrame: DataFrame with Open, High, Low, Close, and Volume.
        """
        stock_data = yf.download(self.stock_symbol, start=self.start_date)

        if stock_data.empty:
            print(
                f"No data found for {self.stock_symbol}. Check the symbol or date range."
            )
            return None

        stock_data = stock_data[["Open", "High", "Low", "Close", "Volume"]]
        stock_data.columns = [col[0] for col in stock_data.columns]
        return stock_data

    def load_news_data(self):
        API_KEY = self.api_keys[0]  # Get from https://newsapi.org/
        current_date = datetime.now()
        date = datetime.strptime(self.start_date, "%Y-%m-%d")
        all_articles = []

        while date <= current_date:
            date_str = date.strftime("%Y-%m-%d")
            print(date_str)
            url = f"https://newsapi.org/v2/everything?q={self.name}&from={date_str}&to={date_str}&sortBy=popularity&apiKey={API_KEY}"
            response = requests.get(url, timeout=10)
            news_data = response.json()
            date += timedelta(days=1)
            if "articles" in news_data:
                articles = news_data["articles"]
                if not articles:
                    break
                all_articles.extend(articles)
            else:
                break

        headlines = [
            (article["title"], article["publishedAt"], article["description"])
            for article in all_articles
        ]
        news_df = pd.DataFrame(headlines, columns=["headline", "date", "description"])
        return news_df

    def load_apitube_data(self):
        API_KEY = self.api_keys[1]
        url = "https://api.apitube.io/v1/news/top-headlines"

        querystring = {
            "title": "Apple",
            "api_key": API_KEY,
            "per_page": 500,
            "published_at.start": "2022-01-01",
            "published_at.end": "NOW",
            "is_duplicate": "true",
            "sort_by": "published_at",
        }
        response = requests.request("GET", url, params=querystring)
        return response.json()
