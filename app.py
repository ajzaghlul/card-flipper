import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Card Flip Analyzer", layout="wide")
st.title("📈 Card Flip Analyzer")

st.write("""
Analyze opportunities to flip raw sports cards for profit by comparing them
with PSA 10 graded prices.
""")

search_query = st.text_input("Enter card name (e.g., Michael Jordan rookie):", "")

if search_query:
    st.header("🔍 Raw Listings")
    
    # --- eBay Scraper ---
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&_sop=12"
    try:
        response = requests.get(ebay_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        for item in soup.select(".s-item"):
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            if title and price:
                listings.append({
                    "Title": title.get_text(strip=True),
                    "Price": price.get_text(strip=True)
                })
        if listings:
            raw_df = pd.DataFrame(listings)
            st.dataframe(raw_df)
        else:
            st.warning("No listings found on eBay.")
    except Exception as e:
        st.error(f"Error fetching eBay listings: {e}")

    # --- Placeholder PSA 10 Price ---
    st.header("💎 PSA 10 Prices")
    psa_10_price = st.number_input("Enter estimated PSA 10 price manually ($):", min_value=0.0, value=100.0, step=5.0)
    st.write(f"Estimated PSA 10 price: ${psa_10_price:.2f}")

    # --- Spread Calculation ---
    if 'raw_df' in locals() and not raw_df.empty:
        try:
            raw_df["Price ($)"] = raw_df["Price"].str.replace(r'[^\d.]', '', regex=True)
            raw_df["Price ($)"] = pd.to_numeric(raw_df["Price ($)"], errors='coerce')
            raw_df = raw_df.dropna(subset=["Price ($)"])
            raw_df["Spread to PSA 10 (%)"] = ((psa_10_price - raw_df["Price ($)"]) / raw_df["Price ($)"]) * 100
            raw_df = raw_df.sort_values("Spread to PSA 10 (%)", ascending=False)
            st.header("📊 Opportunities to Flip")
            st.dataframe(raw_df[["Title", "Price", "Spread to PSA 10 (%)"]])
        except Exception as e:
            st.error(f"Error calculating spread: {e}")

    # --- Sold Price History Chart (Placeholder) ---
    st.header("📈 Sold Price History (Demo)")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=10)
    prices = pd.Series([psa_10_price * (0.9 + 0.2 * (i/10)) for i in range(10)], index=dates)
    fig = px.line(x=prices.index, y=prices.values, labels={"x": "Date", "y": "Sold Price"}, 
                  title=f"Sold Price History for {search_query} (Demo)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please enter a card name to get started.")
