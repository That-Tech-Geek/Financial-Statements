import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import linregress

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T
    
    # Calculate Total Assets if not directly available
    if 'Total Assets' not in balance_sheet.columns:
        balance_sheet['Total Assets'] = balance_sheet['Total Current Assets'] + balance_sheet['Property Plant Equipment'] + balance_sheet['Goodwill'] + balance_sheet['Intangible Assets'] + balance_sheet['Investments'] + balance_sheet['Other Assets']
    
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

def calculate_beta_alpha(historical_data):
    # Calculate daily returns
    historical_data['Returns'] = historical_data['Close'].pct_change()

    # Get market data (e.g., S&P 500) for the same period
    sp500 = yf.Ticker("^GSPC")
    sp500_data = sp500.history(period="max")
    sp500_data = sp500_data.loc[historical_data.index]  # Align dates with the stock data
    sp500_data['Market Returns'] = sp500_data['Close'].pct_change()

    # Perform linear regression to calculate beta and alpha
    valid_data = historical_data.dropna(subset=['Returns'])
    beta, alpha, r_value, p_value, std_err = linregress(sp500_data['Market Returns'].loc[valid_data.index], valid_data['Returns'])
    
    return beta, alpha

def calculate_dcf(balance_sheet, income_statement, discount_rate=0.1):
    # Calculate Free Cash Flow (FCF)
    fcf = income_statement['Net Income'] + income_statement['Depreciation'] - balance_sheet['Capital Expenditures'] - (balance_sheet['Total Current Assets'] - balance_sheet['Total Current Liabilities'])
    
    # Project FCF for the next 5 years (simplified assumption)
    projected_fcf = fcf.mean() * (1 + np.linspace(0.05, 0.02, 5))  # Assuming growth slows down
    
    # Calculate terminal value using a perpetual growth model
    terminal_value = projected_fcf[-1] * (1 + 0.02) / (discount_rate - 0.02)
    
    # Discount FCF and terminal value to present value
    years = np.arange(1, 6)
    discounted_fcf = projected_fcf / (1 + discount_rate) ** years
    discounted_terminal_value = terminal_value / (1 + discount_rate) ** 5
    
    # Calculate Enterprise Value
    enterprise_value = discounted_fcf.sum() + discounted_terminal_value
    
    return enterprise_value

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
            
            # Calculate and display beta and alpha
            beta, alpha = calculate_beta_alpha(historical_data)
            st.write(f"Beta: {beta:.2f}")
            st.write(f"Alpha: {alpha:.2f}")
            
            # Calculate and display DCF analysis result
            enterprise_value = calculate_dcf(balance_sheet, income_statement)
            st.write(f"Discounted Cash Flow (DCF) - Enterprise Value: ${enterprise_value:.2f}")
            
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
