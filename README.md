Gmail API Email Reader with OAuth & PostgreSQL

This project implements a secure email reading pipeline using the Gmail API with OAuth 2.0, stores processed email data in PostgreSQL, and visualizes the data using Streamlit.

Overview

The application authenticates users via OAuth, reads Gmail messages (Inbox and Sent), processes email content and attachments, stores structured data in a PostgreSQL database, and provides a simple UI for viewing stored emails.

Key Features

OAuth 2.0 authentication using Gmail API

Read and process Gmail messages

Extract email body (plain text and HTML)

Download and manage email attachments

Store email data in PostgreSQL

Display stored emails using Streamlit

Technologies Used

Python

Gmail API

OAuth 2.0

PostgreSQL

psycopg2

Streamlit

Pandas

Gmail API & OAuth Workflow

Create a Google Cloud project and enable Gmail API

Generate OAuth Client ID (Desktop Application)

Download and configure credentials.json

User authenticates via browser on first run

Access token is stored securely and reused

Gmail API is accessed using read-only scope

OAuth Scope Used:

https://www.googleapis.com/auth/gmail.readonly

Email Processing Flow

Authenticate using OAuth

Fetch emails using Gmail search queries

Extract sender, subject, and message body

Process forwarded emails and attachments

Store cleaned data in PostgreSQL

Display stored data in Streamlit UI

Database Structure

Emails Table

id | sender | subject | body_text | raw_json


Attachments Table

id | email_id | file_name | file_path

How to Run
python read_email.py
python -m streamlit run app.py

Outcome

Successfully implemented Gmail API with OAuth authentication

Email data stored and managed in PostgreSQL

Interactive data visualization using Streamlit

Google Chat API analysis completed (not implemented due to Workspace limitations)

Author

Pooja
