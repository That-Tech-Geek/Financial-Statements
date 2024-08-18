import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import hashlib
import os

# File to store credentials
CREDENTIALS_FILE = "credentials.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_credentials(username, hashed_password):
    if not os.path.exists(CREDENTIALS_FILE):
        # Create file and write header if it doesn't exist
        with open(CREDENTIALS_FILE, "w") as file:
            file.write("username,password\n")
    
    # Append the new credentials
    with open(CREDENTIALS_FILE, "a") as file:
        file.write(f"{username},{hashed_password}\n")

def check_credentials(username, password):
    if not os.path.exists(CREDENTIALS_FILE):
        return False
    
    hashed_password = hash_password(password)
    
    with open(CREDENTIALS_FILE, "r") as file:
        for line in file:
            stored_username, stored_password = line.strip().split(",")
            if stored_username == username and stored_password == hashed_password:
                return True
    
    return False

def fetch_and_process_data(ticker):
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    historical_data = stock.history(period="max")
    
    # Fetch balance sheet and income statement data
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T

    return historical_data, balance_sheet, income_statement

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

def app():
    st.title("Equity Analysis Jumpstarter")

    # Sidebar for navigation
    option = st.sidebar.selectbox("Select an option", ["Login", "Register"])

    if option == "Register":
        st.subheader("Create an Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if password == confirm_password:
                if not check_credentials(username, password):
                    save_credentials(username, hash_password(password))
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Username already exists. Please choose a different username.")
            else:
                st.error("Passwords do not match.")

    elif option == "Login":
        st.subheader("Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_credentials(username, password):
                st.success("Login successful!")
                # Main application logic
                ticker = st.text_input("Enter the ticker symbol (e.g., AAPL, MSFT):")
                api_key = st.text_input("Enter your NewsAPI key", type="password")

                if ticker and api_key:
                    try:
                        historical_data, balance_sheet, income_statement = fetch_and_process_data(ticker)
                        
                        # Display financial data
                        st.write("Historical Share Price Data:")
                        st.dataframe(historical_data)
                        
                        st.write("Balance Sheet:")
                        st.dataframe(balance_sheet)
                        
                        st.write("Income Statement:")
                        st.dataframe(income_statement)

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
            else:
                st.error("Invalid username or password. Please try again.")

if __name__ == "__main__":
    app()
