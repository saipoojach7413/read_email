import streamlit as st
import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()  # loads .env file

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_email(sender, subject, body, raw_json):
    sql = """
    SELECT id, sender, subject, body_text, created_at
FROM emails
ORDER BY created_at DESC;
"""


    conn = None
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (sender, subject, body, Json(raw_json)))
            row = cur.fetchone()
            conn.commit()
            return row[0]
    except Exception as e:
        print("DB insert error:", e)
    finally:
        if conn:
            conn.close()

    return None
