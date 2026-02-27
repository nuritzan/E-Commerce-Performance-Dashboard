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

# define fungsi RFM
def create_rfm_df(df):
    rfm = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "revenue": "sum"
    })
    rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    # Hitung Recency
    recent_date = df["order_purchase_timestamp"].max().date()
    rfm["max_order_timestamp"] = rfm["max_order_timestamp"].dt.date
    rfm["recency"] = rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm

rfm_df = create_rfm_df(sales_df)

# 3. SIDEBAR
with st.sidebar:
    st.title("🛍️ E-Commerce Dashboard")
    st.markdown("""
    Dashboard ini menyajikan hasil analisis performa penjualan marketplace di brazil pada tahun 2016-2018.
    """)

# 4. HEADER & METRICS
st.title("E-Commerce Performance Dashboard")

total_transaksi = sales_df["order_purchase_timestamp"].count()
total_revenue = sales_df["revenue"].sum()

# Hitung ketepatan pengiriman
on_time = (sales_df["order_delivered_customer_date"] <= sales_df["order_estimated_delivery_date"]).sum()
total_delivery = sales_df["order_delivered_customer_date"].notna().sum()
ketepatan = (on_time / total_delivery) * 100 if total_delivery > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{total_transaksi:,}")
col2.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
col3.metric("Ketepatan Waktu Pengiriman", f"{ketepatan:.2f}%")

st.markdown("---")

# 5. TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Penjualan",
    "📦 Performa Produk",
    "📍 Performa Daerah",
    "💎 RFM Analysis",
    "📝 Conclusion"
])

# TAB 1 - TREND
with tab1:
    st.subheader("Tren Penjualan per Tahun")

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

    st.markdown(f"""
**Insight**
- Penjualan paling banyak adalah di tahun 2018 sebanyak 60,318 transaksi, disusul 2017 sebanyak 49,554 transaksi, dan 2016 sebanyak 317 transaksi.
- Begitu juga dengan revenue yang dihasilkan paling banyak di tahun 2018 dengan total 8,450,534.68, lalu tahun 2017 sebanyak 6,921,206.41, dan terakhir tahun 2016 sebanyak 46,653.74
""")

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

    st.markdown(f"""
**Insight**
- Produk yang paling banyak dibeli adalah bed bath table sebanyak 10.953 buah.
- Sementara itu, produk yang paling banyak menghasilkan revenue adalah health beauty sebanyak 1,412,089.53.""")

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

    st.markdown(f"""
**Insight**
- Kota dengan transaksi terbanyak sekaligus menghasilkan revenue tertinggi adalah sao paulo dengan total transaksi sebanyak 17,400 dan revenue 2,107,960.17.
""")

# TAB 4: RFM ANALYSIS
with tab4:
    st.subheader("Best Customer Based on RFM Parameters")
    
    # Menyiapkan data untuk visualisasi (Nomor urut sebagai pengganti ID panjang)
    rfm_vis = rfm_df.copy()
    
    # Urutkan berdasarkan monetary sebagai standar awal
    rfm_vis = rfm_vis.sort_values(by="monetary", ascending=False).reset_index(drop=True)
    
    # Membuat label nomor (1, 2, 3...) agar sumbu X tidak berantakan kode unik
    rfm_vis["customer_label"] = (rfm_vis.index + 1).astype(str)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Avg Recency (days)", value=avg_recency)
        
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Avg Frequency", value=avg_frequency)
        
    with col3:
        avg_monetary = f"R$ {rfm_df.monetary.mean():,.2f}"
        st.metric("Avg Monetary", value=avg_monetary)

    # Memulai Plotting
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))
    colors = ["#72BCD4"] * 5

    # 1. Best Customers by Recency
    # Kita urutkan berdasarkan recency terkecil (paling baru belanja)
    df_recency = rfm_vis.sort_values(by="recency", ascending=True).head(5)
    sns.barplot(y="recency", x="customer_label", data=df_recency, palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Customer Rank (by Recency)", fontsize=12)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].set_ylim(bottom=0)  # MEMASTIKAN SUMBU Y MULAI DARI 0
    ax[0].tick_params(axis='x', labelsize=12)

    # 2. Best Customers by Frequency
    df_frequency = rfm_vis.sort_values(by="frequency", ascending=False).head(5)
    sns.barplot(y="frequency", x="customer_label", data=df_frequency, palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Customer Rank (by Frequency)", fontsize=12)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=12)

    # 3. Best Customers by Monetary
    df_monetary = rfm_vis.sort_values(by="monetary", ascending=False).head(5)
    sns.barplot(y="monetary", x="customer_label", data=df_monetary, palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("Customer Rank (by Monetary)", fontsize=12)
    ax[2].set_title("By Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=12)

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown(f"""
**Insight**
- Berdasarkan analisis RFM, dapat dilihat bahwa sebagian kecil customer memiliki nilai pembelian yang tinggi dan masih aktif melakukan transaksi, sehingga termasuk dalam kategori pelanggan terbaik. Namun, secara umum frekuensi pembelian customer relatif rendah yang menunjukkan bahwa sebagian besar pelanggan hanya melakukan transaksi satu kali.
""")

# TAB 5 - CONCLUSION
with tab5:
    st.subheader("Conclusion")
    st.success("1. **Pertumbuhan Masif**: Bisnis mengalami pertumbuhan pesat dalam setiap tahunnya terakhir, baik dari sisi jumlah transaksi maupun pendapatan.")
    st.success("2. **Kategori Unggulan**: Kategori **bed_bath_table** memiliki jumlah penjualan terbanyak, sementara kategori **health_beauty** memimpin dalam total pendapatan.")
    st.success("3. **Dominasi Wilayah**: Kota **Sao Paulo** menjadi pusat transaksi terbesar di Brazil.")
    st.success("4. **Strategi Retensi (RFM)**: Mayoritas pelanggan saat ini adalah *One-Time Buyers* (Frequency ≈ 1), sehingga perusahaan perlu berfokus pada strategi retensi dan program loyalitas untuk mengubah pembeli sesekali menjadi pelanggan setia.")

st.caption("Copyright (c) 2026 - M. Muthi' Nuritzan")
