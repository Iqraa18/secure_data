import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Session state initialization
if "cipher" not in st.session_state:
    KEY = Fernet.generate_key()
    st.session_state.cipher = Fernet(KEY)

if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}  # {"ciphertext": {"encrypted_text": x, "passkey": hashed_passkey}}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Function to hash passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text):
    return st.session_state.cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)

    for data in st.session_state.stored_data.values():
        if data["encrypted_text"] == encrypted_text and data["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0
            return st.session_state.cipher.decrypt(encrypted_text.encode()).decode()
    
    st.session_state.failed_attempts += 1
    return None

# Streamlit UI
st.title("🔐 Secure Data Encryption System")

# Sidebar navigation
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome to Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using encryption and passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")

    user_data = st.text_area("Enter your data to encrypt:")
    passkey = st.text_input("Enter a passkey:", type="password")

    if st.button("Encrypt & Store"):
        if user_data and passkey:
            encrypted_text = encrypt_data(user_data)
            hashed_passkey = hash_passkey(passkey)
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            st.success("✅ Data encrypted and stored successfully!")
            st.text(f"🔒 Encrypted Text:\n{encrypted_text}")
        else:
            st.error("⚠️ Please provide both data and passkey.")

elif choice == "Retrieve Data":
    if st.session_state.failed_attempts >= 3:
        st.warning("🔒 Too many failed attempts. Redirecting to Login...")
        st.switch_page("Login")

    st.subheader("🔍 Retrieve Encrypted Data")
    encrypted_text = st.text_area("Enter encrypted text:")
    passkey = st.text_input("Enter your passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_text and passkey:
            decrypted = decrypt_data(encrypted_text, passkey)
            if decrypted:
                st.success(f"✅ Decrypted Data:\n{decrypted}")
            else:
                attempts_left = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey. Attempts left: {attempts_left}")

                if st.session_state.failed_attempts >= 3:
                    st.warning("🚫 Redirecting to login due to too many failed attempts.")
                    st.experimental_rerun()
        else:
            st.error("⚠️ All fields are required.")

elif choice == "Login":
    st.subheader("🔑 Reauthorization")
    login_pass = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if login_pass == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Login successful. You can now retry decryption.")
        else:
            st.error("❌ Incorrect master password.")
