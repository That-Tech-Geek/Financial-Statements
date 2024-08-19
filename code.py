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

def calculate_ratios(balance_sheet, income_statement):
    # Calculate common financial ratios
    
    # Liquidity Ratios
    current_ratio = balance_sheet['Total Current Assets'] / balance_sheet['Total Current Liabilities']
    quick_ratio = (balance_sheet['Total Current Assets'] - balance_sheet['Inventory']) / balance_sheet['Total Current Liabilities']
    cash_ratio = balance_sheet['Cash And Cash Equivalents'] / balance_sheet['Total Current Liabilities']
    
    # Leverage Ratios
    debt_to_equity_ratio = balance_sheet['Total Liabilities'] / balance_sheet['Total Stockholder Equity']
    equity_ratio = balance_sheet['Total Stockholder Equity'] / balance_sheet['Total Assets']
    
    # Profitability Ratios
    gross_profit_margin = income_statement['Gross Profit'] / income_statement['Total Revenue']
    net_profit_margin = income_statement['Net Income'] / income_statement['Total Revenue']
    return_on_equity = income_statement['Net Income'] / balance_sheet['Total Stockholder Equity']
    
    # Efficiency Ratios
    total_assets_turnover = income_statement['Total Revenue'] / balance_sheet['Total Assets']
    fixed_asset_turnover = income_statement['Total Revenue'] / balance_sheet['Property Plant Equipment']

    # Combine all ratios into a DataFrame
    ratios = pd.DataFrame({
        "Current Ratio": current_ratio,
        "Quick Ratio": quick_ratio,
        "Cash Ratio": cash_ratio,
        "Debt-to-Equity Ratio": debt_to_equity_ratio,
        "Equity Ratio": equity_ratio,
        "Gross Profit Margin": gross_profit_margin,
        "Net Profit Margin": net_profit_margin,
        "Return on Equity (ROE)": return_on_equity,
        "Total Assets Turnover": total_assets_turnover,
        "Fixed Asset Turnover": fixed_asset_turnover
    })
    
    return ratios

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
            
            # Display financial data
            st.write("Historical Share Price Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement:")
            st.dataframe(income_statement)
            
            # Calculate and display financial ratios
            ratios = calculate_ratios(balance_sheet, income_statement)
            st.write("Key Financial Ratios:")
            st.dataframe(ratios)
            
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
