import yfinance as yf
import streamlit as st
import pandas as pd
import requests

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

def calculate_net_income(income_statement):
    # Calculate net income based on available columns
    try:
        if not income_statement.empty:
            # Ensure the required columns exist
            required_columns = ['Revenue', 'Cost of Revenue', 'Operating Expenses', 'Interest Expense', 'Income Tax Expense']
            if all(col in income_statement.columns for col in required_columns):
                # Calculate Gross Profit
                income_statement['Gross Profit'] = income_statement['Revenue'] - income_statement['Cost of Revenue']
                
                # Calculate Operating Income
                income_statement['Operating Income'] = income_statement['Gross Profit'] - income_statement['Operating Expenses']
                
                # Calculate Net Income
                income_statement['Net Income'] = income_statement['Operating Income'] - income_statement['Interest Expense'] - income_statement['Income Tax Expense']
                
                # Reset index to ensure 'Date' column is properly handled
                income_statement = income_statement.reset_index()
                income_statement['Date'] = pd.to_datetime(income_statement['Date'])
                income_statement['Year'] = income_statement['Date'].dt.year
                
                # Calculate annual profits
                annual_profits = income_statement.groupby('Year')['Net Income'].sum()
                annual_profits_df = pd.DataFrame(annual_profits).reset_index()
                annual_profits_df.rename(columns={'Net Income': 'Annual Profit'}, inplace=True)
                
                return income_statement, annual_profits_df
            else:
                st.warning("Required columns for net income calculation are missing.")
                return income_statement, pd.DataFrame({'Year': [], 'Annual Profit': []})
        else:
            st.warning("Income statement data is empty.")
            return income_statement, pd.DataFrame({'Year': [], 'Annual Profit': []})
    except Exception as e:
        st.error(f"An error occurred while calculating annual profits: {e}")
        return income_statement, pd.DataFrame({'Year': [], 'Annual Profit': []})

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
            published_at = article.get('publishedAt', 'No date') or 'No date'
            url = article.get('url', '')
            articles.append({
                "Title": title.strip() if title else 'No title',
                "Description": description.strip() if description else 'No description',
                "Published At": published_at.strip() if published_at else 'No date',
                "URL": url
            })
        
        if not articles:
            return [{"Title": "No data available", "Description": "", "Published At": "", "URL": ""}]
        
        return articles
    
    except requests.exceptions.RequestException as e:
        return [{"Title": "Error", "Description": str(e), "Published At": "", "URL": ""}]

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
            
            # Calculate and add annual profits to the income statement
            income_statement, annual_profits_df = calculate_net_income(income_statement)
            
            # Display financial data
            st.write("Historical Share Price Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement with Annual Profits:")
            st.dataframe(income_statement)
            
            st.write("Annual Profits:")
            st.dataframe(annual_profits_df)
            
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
