import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

st.set_page_config(page_title="Gmail Reader", layout="wide")
st.title("📧 Stored Gmail Emails")

# Fetch emails from DB
query = """
SELECT id, sender, subject, body_text, created_at
FROM emails
ORDER BY created_at DESC;
"""

conn = get_conn()
df = pd.read_sql(query, conn)
conn.close()

# Show table
st.dataframe(df)

# View full email
st.subheader("📨 View Email Details")
email_id = st.selectbox("Select Email ID", df["id"])

selected = df[df["id"] == email_id].iloc[0]

st.markdown(f"**From:** {selected['sender']}")
st.markdown(f"**Subject:** {selected['subject']}")
st.text_area("Email Body", selected["body_text"], height=300)
