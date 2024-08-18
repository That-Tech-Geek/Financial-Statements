import yfinance as yf
import streamlit as st
import pandas as pd

def fetch_financials(ticker):
    # Fetch financial data
    stock = yf.Ticker(ticker)
    # Get the last 10 annual financial statements
    annual_reports = stock.financials.T
    if annual_reports.shape[0] > 10:
        annual_reports = annual_reports.head(10)
    return annual_reports

def main():
    st.title("Annual Financial Statements Viewer")
    
    # User input for the ticker
    ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
    
    if ticker:
        st.write(f"Fetching financial statements for ticker: {ticker}")
        try:
            # Fetch and display financial statements
            financials = fetch_financials(ticker)
            st.write("Last 10 Annual Financial Statements:")
            st.dataframe(financials)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
