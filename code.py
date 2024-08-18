import yfinance as yf
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

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

def fetch_legal_cases(ticker):
    # Define the URL for SEC EDGAR search
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example: Extract case information from filings
        cases = []
        for filing in soup.find_all('tr', class_='blueRow') + soup.find_all('tr', class_='whiteRow'):
            columns = filing.find_all('td')
            if len(columns) > 2:
                filing_date = columns[0].text.strip()
                filing_type = columns[1].text.strip()
                filing_description = columns[2].text.strip()
                cases.append({"Filing Date": filing_date, "Type": filing_type, "Description": filing_description})
        
        if not cases:
            return [{"Filing Date": "No data available", "Type": "", "Description": ""}]
        
        return cases
    
    except requests.exceptions.RequestException as e:
        return [{"Filing Date": "Error", "Type": str(e), "Description": ""}]

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
            
            # Display financial data
            st.write("Historical Share Price Data:")
            st.dataframe(historical_data)
            
            st.write("Balance Sheet:")
            st.dataframe(balance_sheet)
            
            st.write("Income Statement:")
            st.dataframe(income_statement)

            # Fetch and display legal cases
            legal_cases = fetch_legal_cases(ticker)
            
            if legal_cases:
                st.write("Legal Cases or Filings:")
                legal_cases_df = pd.DataFrame(legal_cases)
                st.dataframe(legal_cases_df)
            else:
                st.write("No legal cases data available.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
