import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# LOAD DATA
sales_df = pd.read_csv("https://drive.google.com/file/d/1jl0d_NZzdVB8uoPj0Xor768sPDE9cuip/view?usp=drive_link", parse_dates=["order_purchase_timestamp",
                                                        "order_delivered_customer_date",
                                                        "order_estimated_delivery_date"])

# PAGE CONFIG
st.set_page_config(page_title="E-Commerce Performance Dashboard", layout="wide")

st.title("E-Commerce Performance Dashboard")

# SIDEBAR
st.sidebar.header('E-Commerce Performance Dashboard')
st.sidebar.markdown("""
Dashboard ini menyajikan hasil analisis performa penjualan marketplace di brazil pada tahun 2011-2012.
""")


# IKHTISAR DATA
total_transaksi = sales_df["order_id"].nunique()
sales_df["revenue"] = sales_df["price"] + sales_df["freight_value"]
total_revenue = sales_df["revenue"].sum()

on_time = (sales_df["order_delivered_customer_date"] <= sales_df["order_estimated_delivery_date"]).sum()
total_delivery = sales_df["order_delivered_customer_date"].notna().sum()
ketepatan = (on_time / total_delivery) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{total_transaksi:,}")
col2.metric("Total Revenue", f"{total_revenue:,.2f}")
col3.metric("Ketepatan Pengiriman", f"{ketepatan:.2f}%")

st.markdown("---")

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "Tren Penjualan",
    "Performa Produk",
    "Performa Daerah",
    "Conclusion"
])

# TAB 1 - TREND
with tab1:
    st.subheader("Jumlah Transaksi Penjualan per Tahun")

    yearly_transactions = (
        sales_df["order_purchase_timestamp"].dt.year.value_counts().sort_index()
    )

    fig, ax = plt.subplots()
    ax.bar(yearly_transactions.index.astype(str), yearly_transactions.values)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Jumlah Transaksi")
    st.pyplot(fig)

    st.subheader("Jumlah Revenue per Tahun")

    yearly_revenue = (
        sales_df.groupby(sales_df["order_purchase_timestamp"].dt.year)["revenue"].sum()
    )

    fig, ax = plt.subplots()
    ax.bar(yearly_revenue.index.astype(str), yearly_revenue.values)
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Total Revenue")
    st.pyplot(fig)

# TAB 2 - PRODUK
with tab2:
    st.subheader("Top 10 Produk dengan Penjualan Terbanyak")

    top_produk = (
        sales_df["product_category_name_english"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(top_produk.index, top_produk.values)
    ax.set_xlabel("Jumlah Penjualan")
    st.pyplot(fig)

    st.subheader("Top 10 Produk dengan Revenue Tertinggi")

    top_rev_produk = (
        sales_df.groupby("product_category_name_english")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(top_rev_produk.index, top_rev_produk.values)
    ax.set_xlabel("Total Revenue")
    st.pyplot(fig)

# TAB 3 - DAERAH
with tab3:
    st.subheader("Top 10 Kota dengan Transaksi Terbanyak")

    top_city = (
        sales_df["customer_city"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(top_city.index, top_city.values)
    ax.set_xlabel("Jumlah Transaksi")
    st.pyplot(fig)

    st.subheader("Top 10 Kota dengan Revenue Tertinggi")

    top_city_rev = (
        sales_df.groupby("customer_city")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots()
    ax.barh(top_city_rev.index, top_city_rev.values)
    ax.set_xlabel("Total Revenue")
    st.pyplot(fig)

# TAB 4 - CONCLUSION
with tab4:
    st.subheader("Conclusion")
    st.write("""
        1. **Pertumbuhan Masif**: Terjadi lonjakan transaksi signifikan dari tahun 2016 ke 2018, dengan puncak aktivitas ekonomi berada di tahun 2018.

        2. **Kategori Unggulan**: Kategori **health_beauty** menjadi penyumbang pendapatan terbesar bagi perusahaan.

        3. **Dominasi Wilayah**: Kota **Sao Paulo** adalah kontributor utama baik dalam hal jumlah transaksi maupun total pendapatan.
        """)

st.caption("Copyright (c) 2026 - M. Muthi' Nuritzan")
