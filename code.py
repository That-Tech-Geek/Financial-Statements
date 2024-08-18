import yfinance as yf
import streamlit as st
import pandas as pd
import requests

def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch the balance sheet and profit & loss statement
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return balance_sheet, income_statement

def filter_relevant_data(dataframe, keywords):
    # Ensure that the index is a string type for .str accessor
    if not dataframe.index.dtype == 'object':
        dataframe.index = dataframe.index.astype(str)
        
    # Filter rows based on keywords
    relevant_rows = dataframe.loc[dataframe.index.str.contains('|'.join(keywords), case=False, na=False)]
    return relevant_rows

def filter_last_n_years(dataframe, years=10):
    # Convert index to datetime to filter based on the last n years
    dataframe.index = pd.to_datetime(dataframe.index, errors='coerce')
    if dataframe.index.hasnans:
        dataframe = dataframe.dropna(subset=['index'])
    recent_data = dataframe[dataframe.index >= pd.Timestamp.now() - pd.DateOffset(years=years)]
    return recent_data

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

def fetch_news_articles(query, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey=81f1784ea2074e03a558e94c792af540"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Example: Extract relevant information from news articles
        articles = []
        for article in data.get('articles', []):
            title = article.get('title', 'No title') or 'No title'
            description = article.get('description', 'No description') or 'No description'
            published_at = article.get('publishedAt', 'No date') or 'No date'
            articles.append({
                "Title": title.strip() if title else 'No title',
                "Description": description.strip() if description else 'No description',
                "Published At": published_at.strip() if published_at else 'No date'
            })
        
        if not articles:
            return [{"Title": "No data available", "Description": "", "Published At": ""}]
        
        return articles
    
    except requests.exceptions.RequestException as e:
        return [{"Title": "Error", "Description": str(e), "Published At": ""}]

def main():
    st.title("Equity Analysis Jumpstarter")
    st.write("Note that you will need to input the ticker of the company with its relevant suffix, i.e., .NS for NSE, so that you can get your output. There may be incompleteness in the output, which may be either because of the data not being input into the company's financial report for that year, or the data source may be incomplete. Either way, we recommend that you review the dataset and add any data needed by yourself. Thank you.")
    # User input for the ticker
    ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
    
    if ticker and api_key:
        st.write(f"Fetching financial statements for ticker: {ticker}")
        try:
            # Fetch data
            historical_data, balance_sheet, income_statement = fetch_and_process_data(ticker)
            
            # Display financial data
            st.write("Historical Share Price Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement:")
            st.dataframe(income_statement)

            # Fetch and display news articles
            st.write("Fetching news articles related to legal cases...")
            news_articles = fetch_news_articles(ticker, api_key)
            
            if news_articles:
                st.write("News Articles Related to Legal Cases:")
                news_df = pd.DataFrame(news_articles)
                st.dataframe(news_df)
            else:
                st.write("No news articles data available.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
