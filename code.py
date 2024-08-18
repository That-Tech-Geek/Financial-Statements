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
            
            # Define keywords to look for
            income_keywords = ["Profit After Tax", "EBITDA", "Net Income", "Operating Income", "Gross Profit"]
            balance_keywords = ["Total Assets", "Total Liabilities", "Shareholder Equity", "Current Assets", "Current Liabilities"]

            # Filter data
            filtered_balance_sheet = filter_relevant_data(balance_sheet, balance_keywords)
            filtered_income_statement = filter_relevant_data(income_statement, income_keywords)
            
            st.write("Last 10 Annual Balance Sheets:")
            st.dataframe(filtered_balance_sheet.head(10))

            st.write("Last 10 Annual Profit & Loss Statements:")
            st.dataframe(filtered_income_statement.head(10))
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
