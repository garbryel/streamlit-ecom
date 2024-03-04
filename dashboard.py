import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
#all_order_df = pd.read_csv("all_order.csv")
url='https://drive.google.com/file/d/1KQ1NA0lrXsEb-AbGmnhbjcu8nd50eUxp/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
all_order_df = pd.read_csv(url)


# Konversi kolom tanggal ke tipe data datetime jika belum
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
for column in datetime_columns:
    all_order_df[column] = pd.to_datetime(all_order_df[column])

# Helper function to create DataFrame by state
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bystate_df

# Helper function to create DataFrame by city
def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bycity_df

# Helper function to create DataFrame by product category
def create_byproductcategory_df(df):
    bycategory_df = df.groupby(by="product_category_name_english").order_id.nunique().reset_index()
    bycategory_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return bycategory_df

# Helper function to create DataFrame by order status
def create_byorderstatus_df(df):
    byorderstatus_df = df.groupby(by="order_status").order_id.nunique().reset_index()
    byorderstatus_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return byorderstatus_df

# Helper function to create DataFrame by review score
def create_byreviewscore_df(df):
    byreviewscore_df = df.groupby(by="review_score").order_id.nunique().reset_index()
    byreviewscore_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return byreviewscore_df

    
# Helper function to create RFM DataFrame
def create_rfm_df(df):
    # Calculate Recency
    current_date = df['order_purchase_timestamp'].max()
    recency_df = df.groupby('customer_id')['order_purchase_timestamp'].max().reset_index()
    recency_df['Recency'] = (current_date - recency_df['order_purchase_timestamp']).dt.days
    
    # Calculate Frequency
    frequency_df = df.groupby('customer_id').size().reset_index(name='Frequency')
    
    # Calculate Monetary
    monetary_df = df.groupby('customer_id')['price'].sum().reset_index()
    
    # Merge all three
    rfm_df = pd.merge(recency_df[['customer_id', 'Recency']], frequency_df, on='customer_id')
    rfm_df = pd.merge(rfm_df, monetary_df.rename(columns={'price': 'Monetary'}), on='customer_id')
    
    return rfm_df

# Visualisasi RFM Analysis
def visualize_rfm_analysis(rfm_df):
    # Visualisasi Recency
    st.subheader("By Recency")
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm_df['Recency'], kde=True, color='skyblue')
    plt.title("By Recency")
    st.pyplot(plt)

    # Visualisasi Frequency
    st.subheader("By Frequency")
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm_df['Frequency'], bins=20, kde=True, color='skyblue')
    plt.title("By Frequency")
    st.pyplot(plt)

    # Visualisasi Monetary
    st.subheader("By Monetary")
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm_df['Monetary'], bins=20, kde=True, color='skyblue')
    plt.title("By Monetary")
    st.pyplot(plt)

# Add title to your app
st.title('E-commerce Dashboard')


# Add a sidebar

# Sorting and resetting index
all_order_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_order_df.reset_index(drop=True, inplace=True)

# Get min and max dates
min_date_order = all_order_df["order_purchase_timestamp"].min()
max_date_order = all_order_df["order_purchase_timestamp"].max()

min_date_delivery = all_order_df["order_delivered_customer_date"].min()
max_date_delivery = all_order_df["order_delivered_customer_date"].max()

# Filter by order date in sidebar
start_date_order, end_date_order = st.sidebar.date_input('Order Date Range', min_value=min_date_order,
                                                         max_value=max_date_order,
                                                         value=[min_date_order, max_date_order])

# Filter by delivery date in sidebar
start_date_delivery, end_date_delivery = st.sidebar.date_input('Delivery Date Range', min_value=min_date_delivery,
                                                               max_value=max_date_delivery,
                                                               value=[min_date_delivery, max_date_delivery])

# Convert date input to datetime
start_date_order = pd.Timestamp(start_date_order)
end_date_order = pd.Timestamp(end_date_order)

start_date_delivery = pd.Timestamp(start_date_delivery)
end_date_delivery = pd.Timestamp(end_date_delivery)

# Filter data based on selected dates
filtered_orders = all_order_df[(all_order_df['order_purchase_timestamp'] >= start_date_order) & 
                               (all_order_df['order_purchase_timestamp'] <= end_date_order) &
                               (all_order_df['order_delivered_customer_date'] >= start_date_delivery) &
                               (all_order_df['order_delivered_customer_date'] <= end_date_delivery)]


# Add subheader for visualizations
st.subheader('Visualization')

# Visualisasi untuk top 10 kategori produk yang paling banyak diminati
st.subheader("Top 10 Most Popular Product Categories")
popular_data = all_order_df.groupby(by="product_category_name_english").order_id.nunique().sort_values(ascending=True).tail(10)
plt.figure(figsize=(10,5))
plt.barh(popular_data.index[:-1], popular_data.values[:-1], color='lightgray')
plt.barh(popular_data.index[-1:], popular_data.values[-1:], color='skyblue')
plt.title('Top 10 Popular Category')
st.pyplot(plt)

# Visualisasi untuk jumlah pelanggan berdasarkan kota
st.subheader("Number of Customers by Cities")
bycity_df = all_order_df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=True).tail(10)
plt.figure(figsize=(10,5))
plt.barh(bycity_df.index[:-1], bycity_df.values[:-1], color='lightgray')
plt.barh(bycity_df.index[-1:], bycity_df.values[-1:], color='skyblue')
plt.title('Number of Customer by Cities')
st.pyplot(plt)

# Visualisasi untuk jumlah pelanggan berdasarkan negara bagian
st.subheader("Number of Customers by States")
bystate_df = all_order_df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=True).tail(10)
plt.figure(figsize=(10,5))
plt.barh(bystate_df.index[:-1], bystate_df.values[:-1], color='lightgray')
plt.barh(bystate_df.index[-1:], bystate_df.values[-1:], color='skyblue')
plt.title('Number of Customer by States')
st.pyplot(plt)

# Visualisasi untuk distribusi review skor
st.subheader("Review Scores")
plt.figure(figsize=(10, 6))
all_order_df['review_score'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.xticks(rotation=360)
plt.title("Review Scores")
st.pyplot(plt)

# Visualisasi untuk distribusi status pesanan
st.subheader("Order Status")
plt.figure(figsize=(10, 6))
all_order_df['order_status'].value_counts().plot(kind='bar', color='skyblue')
plt.xticks(rotation=360)
plt.title("Order Status")
st.pyplot(plt)

# Gunakan helper function untuk membuat RFM DataFrame
rfm_df = create_rfm_df(all_order_df)

# Gunakan helper function untuk visualisasi RFM Analysis
visualize_rfm_analysis(rfm_df)