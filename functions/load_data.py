import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import pandas as pd


class LoadData:
    def __init__(self, stock_symbol):
        """
        Initializes the LoadData class with a stock symbol.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., 'AAPL').
        """
        self.stock_symbol = stock_symbol
        self.start_date = (datetime.now() - timedelta(weeks=4)).strftime("%Y-%m-%d")
        self.api_key = self.load_api_key()
        ticker = yf.Ticker(self.stock_symbol)
        self.name = ticker.info["displayName"]

    def load_api_key(self):
        """
        Loads the API key from the .env file.

        Returns:
            str: The API key.
        """
        load_dotenv()  # Load environment variables from .env
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API Key not found. Check your .env file.")
        return api_key

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
        API_KEY = self.load_api_key()  # Get from https://newsapi.org/
        current_date = datetime.now()
        date = datetime.strptime(self.start_date, "%Y-%m-%d")
        all_articles = []

        while date <= current_date:
            date_str = date.strftime("%Y-%m-%d")
            print(date_str)
            url = f"https://newsapi.org/v2/everything?q={self.name}&from={date_str}&to={date_str}&sortBy=popularity&apiKey={API_KEY}"
            response = requests.get(url)
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
            (article["title"], article["publishedAt"]) for article in all_articles
        ]
        news_df = pd.DataFrame(headlines, columns=["headline", "date"])
        return news_df
