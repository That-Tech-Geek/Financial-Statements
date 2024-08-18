import yfinance as yf
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

def plot_correlation_heatmap(dataframe, title):
    # Calculate correlation matrix
    correlation_matrix = dataframe.corr()
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1)
    plt.title(title)
    plt.tight_layout()
    st.pyplot(plt)

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

def main():
    st.title("Company Financial Statements Viewer")
    
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

            # Filter for the last 10 years
            filtered_balance_sheet_last_10_years = filter_last_n_years(filtered_balance_sheet)
            filtered_income_statement_last_10_years = filter_last_n_years(filtered_income_statement)

            st.write("Filtered Balance Sheet Data (Last 10 Years):")
            st.dataframe(filtered_balance_sheet_last_10_years)

            st.write("Filtered Income Statement Data (Last 10 Years):")
            st.dataframe(filtered_income_statement_last_10_years)

            # Plot correlation heatmaps
            st.write("Correlation Heatmap for Balance Sheet Data:")
            plot_correlation_heatmap(filtered_balance_sheet_last_10_years, 'Balance Sheet Data Correlation Heatmap')

            st.write("Correlation Heatmap for Income Statement Data:")
            plot_correlation_heatmap(filtered_income_statement_last_10_years, 'Income Statement Data Correlation Heatmap')
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
