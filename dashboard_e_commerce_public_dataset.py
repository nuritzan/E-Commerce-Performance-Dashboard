import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. CONFIG HALAMAN
st.set_page_config(
    page_title="E-Commerce Performance Dashboard", 
    page_icon="🛍️",
    layout="wide"
)

# 2. LOAD DATA
@st.cache_data
def load_data():
    # Gunakan try-except agar tidak error jika path folder berbeda
    try:
        df = pd.read_csv("sales_df.csv", parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ])
    except FileNotFoundError:
        df = pd.read_csv("sales_df.csv", parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ])
    
    # Tambahkan kolom revenue
    if "revenue" not in df.columns:
        df["revenue"] = df["price"] + df["freight_value"]
    return df

# Memanggil data
try:
    sales_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.title("🛍️ E-Commerce Dashboard")
    st.markdown("""
    Analisis performa penjualan marketplace di Brazil.
    """)
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

# 4. HEADER & METRICS
st.title("E-Commerce Performance Dashboard")

total_transaksi = sales_df["order_id"].nunique()
total_revenue = sales_df["revenue"].sum()

# Hitung ketepatan pengiriman
on_time = (sales_df["order_delivered_customer_date"] <= sales_df["order_estimated_delivery_date"]).sum()
total_delivery = sales_df["order_delivered_customer_date"].notna().sum()
ketepatan = (on_time / total_delivery) * 100 if total_delivery > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{total_transaksi:,}")
col2.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
col3.metric("Ketepatan Pengiriman", f"{ketepatan:.2f}%")

st.markdown("---")

# 5. TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tren Penjualan",
    "📦 Performa Produk",
    "📍 Performa Daerah",
    "📝 Conclusion"
])

# TAB 1 - TREND
with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Transaksi per Tahun")
        yearly_transactions = sales_df["order_purchase_timestamp"].dt.year.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=yearly_transactions.index, y=yearly_transactions.values, palette="Blues_d", ax=ax)
        st.pyplot(fig)

    with col_b:
        st.subheader("Revenue per Tahun")
        yearly_revenue = sales_df.groupby(sales_df["order_purchase_timestamp"].dt.year)["revenue"].sum()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=yearly_revenue.index, y=yearly_revenue.values, palette="Greens_d", ax=ax)
        st.pyplot(fig)

# TAB 2 - PRODUK
with tab2:
    st.subheader("Analisis Top 10 Kategori Produk")
    col_c, col_d = st.columns(2)

    with col_c:
        top_produk = sales_df["product_category_name_english"].value_counts().head(10).sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(10, 8))
        top_produk.plot(kind='barh', color='#72BCD4', ax=ax)
        ax.set_title("Penjualan Terbanyak")
        st.pyplot(fig)

    with col_d:
        top_rev_produk = sales_df.groupby("product_category_name_english")["revenue"].sum().sort_values(ascending=False).head(10).sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=(10, 8))
        top_rev_produk.plot(kind='barh', color='#88c999', ax=ax)
        ax.set_title("Revenue Tertinggi")
        st.pyplot(fig)

# TAB 3 - DAERAH
with tab3:
    st.subheader("Geografi Penjualan (Top 10 Kota)")
    top_city = sales_df["customer_city"].value_counts().head(10).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=top_city.values, y=top_city.index, palette="rocket", ax=ax)
    st.pyplot(fig)

# TAB 4 - CONCLUSION
with tab4:
    st.subheader("Conclusion")
    st.success("1. **Pertumbuhan Masif**: Terjadi lonjakan transaksi signifikan hingga puncak di tahun 2018.")
    st.success("2. **Kategori Unggulan**: Kategori **health_beauty** memimpin dalam total pendapatan.")
    st.success("3. **Dominasi Wilayah**: Kota **Sao Paulo** tetap menjadi pusat transaksi terbesar.")

st.caption("Copyright (c) 2026 - M. Muthi' Nuritzan")
