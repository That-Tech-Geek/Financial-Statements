from cryptography.fernet import Fernet
import json
import streamlit as st

def generate_key():
    return Fernet.generate_key()

def get_key():
    if 'key' not in st.session_state:
        st.session_state.key = generate_key()
    return st.session_state.key

def encrypt_message(message, key):
    fernet = Fernet(key)
    return fernet.encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_message).decode()

def save_data(data, key):
    encrypted_data = encrypt_message(json.dumps(data), key)
    st.session_state.encrypted_data = encrypted_data

def load_data(key):
    if 'encrypted_data' in st.session_state:
        return json.loads(decrypt_message(st.session_state.encrypted_data, key))
    return {}
