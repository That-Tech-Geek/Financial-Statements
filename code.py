import yfinance as yf
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

def check_missing_data(df):
    missing_data = df.isna().sum()
    return missing_data[missing_data > 0]

def search_missing_data(query):
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    for item in soup.find_all('div', class_='BNeawe iBp4i AP7Wnd'):
        text = item.get_text()
        data.append(text)
    
    return data

def update_dataset_with_fetched_data(df, fetched_data, column_name):
    df[column_name] = fetched_data
    return df

def calculate_net_income(income_statement):
    try:
        if not income_statement.empty:
            available_columns = income_statement.columns.tolist()
            st.write(f"Available columns in the income statement: {available_columns}")

            income_statement['Net Income'] = pd.NA
            
            if 'Gross Profit' in available_columns and 'Operating Expenses' in available_columns:
                income_statement['Net Income'] = (
                    income_statement['Gross Profit'] 
                    - income_statement['Operating Expenses']
                )
            elif 'Revenue' in available_columns and 'Operating Expenses' in available_columns and 'Total Expenses' in available_columns:
                income_statement['Net Income'] = (
                    income_statement['Revenue']
                    - income_statement['Total Expenses']
                )
            else:
                st.warning("Required columns for calculating Net Income are missing.")

            income_statement = income_statement.reset_index()
            income_statement['Date'] = pd.to_datetime(income_statement['Date'])
            income_statement['Year'] = income_statement['Date'].dt.year

            annual_profits = income_statement.groupby('Year')['Net Income'].sum()
            annual_profits_df = pd.DataFrame(annual_profits).reset_index()
            annual_profits_df.rename(columns={'Net Income': 'Annual Profit'}, inplace=True)
            
            return income_statement, annual_profits_df
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
            
            # Check and search for missing data
            missing_data = check_missing_data(income_statement)
            if not missing_data.empty:
                st.write(f"Missing data detected: {missing_data}")
                for column in missing_data.index:
                    query = f"{ticker} {column} financial data"
                    fetched_data = search_missing_data(query)
                    income_statement = update_dataset_with_fetched_data(income_statement, fetched_data, column)
            
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
