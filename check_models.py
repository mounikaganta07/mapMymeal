import requests
import streamlit as st

# Read OpenRouter API key from secrets
openrouter_key = st.secrets["OPENROUTER_API_KEY"]

url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {openrouter_key}"}

resp = requests.get(url, headers=headers)

print("Status:", resp.status_code)
print("Content-Type:", resp.headers.get("Content-Type", ""))
print(resp.json())
