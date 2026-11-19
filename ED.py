import streamlit as st    
import pandas as pd
import plotly.express as px    
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly_white"
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")
st.title("📊 E-commerce Sales & Profit Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        data = pd.read_csv(uploaded_file, encoding='latin-1')
        required_cols = [
            'Order Date', 'Ship Date', 'Sales', 'Profit', 'Category',
            'Sub-Category', 'Segment', 'Region', 'Discount', 'Quantity', 'Product Name'
        ]
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
            st.stop()

    
        data['Order Date'] = pd.to_datetime(data['Order Date'], errors='coerce')
        data['Ship Date'] = pd.to_datetime(data['Ship Date'], errors='coerce')
    
        data = data.dropna(subset=['Order Date', 'Ship Date'])

      
        data['Order Month'] = data['Order Date'].dt.month
        data['Order Year'] = data['Order Date'].dt.year
        data['Order Day'] = data['Order Date'].dt.dayofweek
        data.drop_duplicates(inplace=True)

        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        data['Order Month Name'] = data['Order Month'].map(month_map)

        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Monthly Trends",
            "📦 Category/Sub-Category",
            "👥 Segment & Region",
            "🧪 Scatter & Products"
        ])

        with tab1:
            st.subheader("Monthly Sales & Profit")
            sales_by_month = data.groupby('Order Month Name')['Sales'].sum().reindex(list(month_map.values())).reset_index()
            profit_by_month = data.groupby('Order Month Name')['Profit'].sum().reindex(list(month_map.values())).reset_index()

            remove_months = st.multiselect(
                "Hide specific months from charts:",
                options=sales_by_month["Order Month Name"].tolist()
            )
            sales_by_month = sales_by_month[~sales_by_month["Order Month Name"].isin(remove_months)]
            profit_by_month = profit_by_month[~profit_by_month["Order Month Name"].isin(remove_months)]

            fig1 = px.line(sales_by_month,
                           x='Order Month Name', y='Sales',
                           title='Monthly Sales Analysis')
            fig2 = px.line(profit_by_month,
                           x='Order Month Name', y='Profit',
                           title='Monthly Profit Analysis')

            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.subheader("Sales & Profit by Category/Sub-Category")
            sales_by_category = data.groupby('Category')['Sales'].sum().reset_index()
            sales_by_subcategory = data.groupby('Sub-Category')['Sales'].sum().reset_index()
            profit_by_category = data.groupby('Category')['Profit'].sum().reset_index()
            profit_by_subcategory = data.groupby('Sub-Category')['Profit'].sum().reset_index()

            remove_cat = st.multiselect("Hide Categories:", options=sales_by_category["Category"].tolist())
            remove_subcat = st.multiselect("Hide Sub-Categories:", options=sales_by_subcategory["Sub-Category"].tolist())

            sales_by_category = sales_by_category[~sales_by_category["Category"].isin(remove_cat)]
            profit_by_category = profit_by_category[~profit_by_category["Category"].isin(remove_cat)]
            sales_by_subcategory = sales_by_subcategory[~sales_by_subcategory["Sub-Category"].isin(remove_subcat)]
            profit_by_subcategory = profit_by_subcategory[~profit_by_subcategory["Sub-Category"].isin(remove_subcat)]


            fig3 = px.pie(sales_by_category, values='Sales', names='Category',
                          title='Sales Analysis by Category', hole=0.2)
            fig3.update_traces(textinfo='percent+label+value')
            fig3.update_layout(title_font_size=24)

            fig4 = px.bar(sales_by_subcategory,
                          x='Sub-Category', y='Sales',
                          title='Sales Analysis by Sub-Category')

            fig5 = px.bar(profit_by_category,
                          x='Category', y='Profit',
                          color='Category', title='Profit Analysis by Category')

            fig6 = px.bar(profit_by_subcategory,
                          x='Sub-Category', y='Profit',
                          color='Sub-Category', title='Profit Analysis by Sub-Category')

            st.plotly_chart(fig3, use_container_width=True)
            st.plotly_chart(fig4, use_container_width=True)
            st.plotly_chart(fig5, use_container_width=True)
            st.plotly_chart(fig6, use_container_width=True)

        with tab3:
            st.subheader("Segment & Region Analysis")
            sales_profit_by_segment = data.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
            sales_region = data.groupby(["Region", "Category"])["Sales"].sum().reset_index()

            remove_segments = st.multiselect("Hide Segments:", options=sales_profit_by_segment["Segment"].tolist())
            sales_profit_by_segment = sales_profit_by_segment[~sales_profit_by_segment["Segment"].isin(remove_segments)]

            fig7 = go.Figure()
            fig7.add_trace(go.Bar(x=sales_profit_by_segment['Segment'],
                                  y=sales_profit_by_segment['Sales'], name='Sales'))
            fig7.add_trace(go.Bar(x=sales_profit_by_segment['Segment'],
                                  y=sales_profit_by_segment['Profit'], name='Profit'))
            fig7.update_layout(title='Sales and Profit Analysis by Customer Segment',
                              xaxis_title='Customer Segment', yaxis_title='Amount', barmode='group')

            fig8 = px.density_heatmap(sales_region,
                                      x="Region", y="Category", z="Sales",
                                      color_continuous_scale="Viridis",
                                      title="Sales by Region & Category")

            st.plotly_chart(fig7, use_container_width=True)
            st.plotly_chart(fig8, use_container_width=True)

        with tab4:
            st.subheader("Discount Impact & Top Products")
            fig9 = px.scatter(data, x='Sales', y='Profit',
                              color='Category', size='Quantity',
                              title='Profit vs Sales (bubble = Quantity)')

            fig10 = px.scatter(data, x="Discount", y="Profit",
                               color="Sales", title="Discount vs Profit")

            top_products = data.groupby("Product Name")["Sales"].sum().nlargest(10).reset_index()

            remove_products = st.multiselect("Hide Products:", options=top_products["Product Name"].tolist())
            top_products = top_products[~top_products["Product Name"].isin(remove_products)]

            fig11 = px.bar(top_products, x="Product Name", y="Sales",
                           title="Top 10 Products by Sales")

            st.plotly_chart(fig9, use_container_width=True)
            st.plotly_chart(fig10, use_container_width=True)
            st.plotly_chart(fig11, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading or processing file: {e}")
        st.stop()