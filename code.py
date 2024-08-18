import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from cryptography.fernet import Fernet

# Access user credentials and key from Streamlit secrets
KEY = st.secrets["encryption_key"].encode()
fernet = Fernet(KEY)
USER_CREDENTIALS_ENCRYPTED = st.secrets["user_credentials"]

def encrypt_password(password):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return fernet.decrypt(encrypted_password.encode()).decode()

def check_credentials(username, password):
    encrypted_password = USER_CREDENTIALS_ENCRYPTED.get(username)
    if encrypted_password:
        return decrypt_password(encrypted_password) == password
    return False

def register_user(username, password):
    if username in USER_CREDENTIALS_ENCRYPTED:
        return "Username already exists. Please choose a different username."
    encrypted_password = encrypt_password(password)
    USER_CREDENTIALS_ENCRYPTED[username] = encrypted_password
    return "Registration successful! You can now log in."

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
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    st.title("Equity Analysis Jumpstarter")

    if not st.session_state.logged_in:
        # Show login or registration page
        option = st.sidebar.selectbox("Select an option", ["Login", "Register"])

        if option == "Register":
            st.subheader("Create an Account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Register"):
                if password == confirm_password:
                    message = register_user(username, password)
                    st.success(message) if "successful" in message else st.error(message)
                else:
                    st.error("Passwords do not match.")

        elif option == "Login":
            st.subheader("Log In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if check_credentials(username, password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success("Login successful!")
                    st.experimental_rerun()  # Refresh to show main application
                else:
                    st.error("Invalid username or password. Please try again.")
    else:
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
    app()
