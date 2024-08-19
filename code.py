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
    ratios = {}
    
    try:
        # Liquidity Ratios
        current_ratio = balance_sheet['Total Current Assets'] / balance_sheet['Total Current Liabilities']
        quick_ratio = (balance_sheet['Total Current Assets'] - balance_sheet['Inventory']) / balance_sheet['Total Current Liabilities']
        cash_ratio = balance_sheet['Cash'] / balance_sheet['Total Current Liabilities']
        
        # Leverage Ratios
        debt_to_equity = balance_sheet['Total Liabilities'] / balance_sheet['Total Stockholder Equity']
        equity_ratio = balance_sheet['Total Stockholder Equity'] / balance_sheet['Total Assets']
        debt_to_assets = balance_sheet['Total Liabilities'] / balance_sheet['Total Assets']
        
        # Profitability Ratios
        gross_profit_margin = income_statement['Gross Profit'] / income_statement['Total Revenue']
        net_profit_margin = income_statement['Net Income'] / income_statement['Total Revenue']
        return_on_assets = income_statement['Net Income'] / balance_sheet['Total Assets']
        return_on_equity = income_statement['Net Income'] / balance_sheet['Total Stockholder Equity']
        
        # Efficiency Ratios
        asset_turnover = income_statement['Total Revenue'] / balance_sheet['Total Assets']
        inventory_turnover = income_statement['Cost Of Revenue'] / balance_sheet['Inventory']
        
        ratios = {
            "Current Ratio": current_ratio,
            "Quick Ratio": quick_ratio,
            "Cash Ratio": cash_ratio,
            "Debt to Equity Ratio": debt_to_equity,
            "Equity Ratio": equity_ratio,
            "Debt to Assets Ratio": debt_to_assets,
            "Gross Profit Margin": gross_profit_margin,
            "Net Profit Margin": net_profit_margin,
            "Return on Assets": return_on_assets,
            "Return on Equity": return_on_equity,
            "Asset Turnover": asset_turnover,
            "Inventory Turnover": inventory_turnover
        }
    except KeyError as e:
        st.warning(f"Some data for ratio calculation is missing: {e}")
    
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
            st.write("Financial Ratios:")
            ratios = calculate_ratios(balance_sheet, income_statement)
            if ratios:
                st.dataframe(pd.DataFrame(ratios).T)
            else:
                st.write("Ratios could not be calculated due to missing data.")

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
