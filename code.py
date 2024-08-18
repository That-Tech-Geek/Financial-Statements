import streamlit as st

# Access user credentials from Streamlit secrets
USER_CREDENTIALS = st.secrets["credentials"]

def check_credentials(username, password):
    # Check if username exists and password matches
    return USER_CREDENTIALS.get(username) == password

def app():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    st.title("Equity Analysis Jumpstarter")

    if not st.session_state.logged_in:
        # Show login page
        st.subheader("Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()  # Refresh to show main application
            else:
                st.error("Invalid username or password. Please try again.")
    else:
        # Main application logic
        st.write("You are logged in!")
        # Add your main application code here

if __name__ == "__main__":
    app()
