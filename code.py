import yfinance as yf
import streamlit as st
import pandas as pd
import requests
from langdetect import detect, LangDetectException
from textblob import TextBlob

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return 'Positive' if analysis.sentiment.polarity > 0 else 'Negative' if analysis.sentiment.polarity < 0 else 'Neutral'

def fetch_news_articles(query, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&language=en"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant information from news articles
        articles = []
        for article in data.get('articles', []):
            title = article.get('title', 'No title') or 'No title'
            description = article.get('description', 'No description') or 'No description'
            content = article.get('content', 'No content') or 'No content'
            url = article.get('url', '')
            
            if is_english(title + " " + description + " " + content):
                sentiment = analyze_sentiment(content)
                articles.append({
                    "Title": title.strip(),
                    "Description": description.strip(),
                    "Sentiment": sentiment,
                    "Published At": article.get('publishedAt', 'No date').strip(),
                    "URL": url
                })
        
        if not articles:
            return [{"Title": "No data available", "Description": "", "Sentiment": "", "Published At": "", "URL": ""}]
        
        return articles
    
    except requests.exceptions.RequestException as e:
        return [{"Title": "Error", "Description": str(e), "Sentiment": "", "Published At": "", "URL": ""}]

def main():
    st.title("Equity Analysis Jumpstarter")
    st.write("Note that you will need to input the ticker of the company with its relevant suffix, i.e., .NS for NSE, so that you can get your output. There may be incompleteness in the output, which may be either because of the data not being input into the company's financial report for that year, or the data source may be incomplete. Either way, we recommend that you review the dataset and add any data needed by yourself. Thank you.")
    
    # User input for the ticker and API key
    ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
    api_key = "81f1784ea2074e03a558e94c792af540"  # Your NewsAPI key
    
    if ticker:
        st.write(f"Fetching financial statements for ticker: {ticker}")
        try:
            # Fetch financial data
            historical_data, balance_sheet, income_statement = fetch_and_process_data(ticker)
            
            # Display financial data
            st.write("Historical Share Price Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement:")
            st.dataframe(income_statement)

            # Fetch and display news articles
            st.write("Fetching news articles related to the company...")
            news_articles = fetch_news_articles(ticker, api_key)
            
            if news_articles:
                st.write("News Articles Related to the Company:")
                news_df = pd.DataFrame(news_articles)
                st.dataframe(news_df)
            else:
                st.write("No news articles data available.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
