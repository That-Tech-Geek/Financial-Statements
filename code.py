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

def main():
    st.title("Equity Analysis Jumpstarter")
    st.write("Note that you will need to input the ticker of the company with its relevant suffix, i.e., .NS for NSE, so that you can get your output. There may be incompleteness in the output, which may be either because of the data not being input into the company's financial report for that year, or the data source may be incomplete. Either way, we recommend that you review the dataset and add any data needed by yourself. Thank you.")
    
    # User input for the ticker
    ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
    
    if ticker:
        st.write(f"Fetching financial statements for ticker: {ticker}")
        try:
            # Fetch data
            historical_data, balance_sheet, income_statement = fetch_and_process_data(ticker)
            
            # Print data to debug
            st.write("Historical Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement:")
            st.dataframe(income_statement)

            # Define keywords to look for
            income_keywords = ["Profit After Tax", "EBITDA", "Net Income", "Operating Income", "Gross Profit"]
            balance_keywords = ["Total Assets", "Total Liabilities", "Shareholder Equity", "Current Assets", "Current Liabilities"]
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
