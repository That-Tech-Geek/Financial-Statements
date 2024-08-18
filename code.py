import yfinance as yf
import streamlit as st
import pandas as pd

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

def main():
    st.title("Company Financial Statements Viewer")
    
    # User input for the ticker
    ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
    
    if ticker:
        st.write(f"Fetching financial statements for ticker: {ticker}")
        try:
            # Fetch data
            balance_sheet, income_statement = fetch_data(ticker)
            
            # Print data to debug
            st.write("Balance Sheet Data (Raw):")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement Data (Raw):")
            st.dataframe(income_statement)

            # Define keywords to look for
            income_keywords = ["Profit After Tax", "EBITDA", "Net Income", "Operating Income", "Gross Profit"]
            balance_keywords = ["Total Assets", "Total Liabilities", "Shareholder Equity", "Current Assets", "Current Liabilities"]

            # Filter data
            filtered_balance_sheet = filter_relevant_data(balance_sheet, balance_keywords)
            filtered_income_statement = filter_relevant_data(income_statement, income_keywords)
            
            # Sort by date and get the most recent 10 years
            filtered_balance_sheet = filtered_balance_sheet.sort_index(ascending=False)
            filtered_income_statement = filtered_income_statement.sort_index(ascending=False)

            st.write("Filtered Balance Sheet Data (Last 10 Years):")
            st.dataframe(filtered_balance_sheet.head(10))

            st.write("Filtered Income Statement Data (Last 10 Years):")
            st.dataframe(filtered_income_statement.head(10))
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
