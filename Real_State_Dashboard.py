
# Import Helper Libraries 
import streamlit as st
import pandas as pd 
import plotly.express as px 
import plotly.io as pio

custom_template = pio.templates["plotly"].update({
    "layout": {
        "colorway": px.colors.sequential.Burg,  # set of categorical colors
    }
})

pio.templates["my_theme"] = custom_template
pio.templates.default = "my_theme"

# Page Config
st.set_page_config(layout='wide', page_title="Real State Analysis")


# -------------------------------
# CUSTOM CSS — FULL WIDTH + CENTER
# -------------------------------
st.markdown("""
<style>

/* Title فقط (st.title) باللون الأحمر الخاص بـ Plotly */
h1 {
    color: #EF553B !important;   /* Red-Orange used by Plotly */
    text-align: center !important;
}

/* باقي التنسيقات */
.block-container {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 4rem !important;
    padding-right: 4rem !important;
}

p {
    text-align: center !important;
}

[data-testid="metric-container"] {
    text-align: center !important;
    margin: auto !important;
}

.stPlotlyChart {
    margin: auto !important;
}

.css-1kyxreq, .element-container {
    margin-left: auto !important;
    margin-right: auto !important;
}

</style>
""", unsafe_allow_html=True)




# -------------------------
# READ DATA
# -------------------------
data = pd.read_csv("end EDA.csv")


# -------------------------------
# NUMBER FORMATTER (K / M)
# -------------------------------
def format_number(num):
    """Convert large numbers into K/M format."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"


# Sidebar filter
typee = st.sidebar.multiselect('Filter By Type', options=data['type'].unique())
typee = data['type'].unique() if typee == [] else typee

bedrooms_num = st.sidebar.multiselect('Filter By Bedrooms', options=data['bedrooms_num'].unique())
bedrooms_num = data['bedrooms_num'].unique() if bedrooms_num == [] else bedrooms_num

bathrooms = st.sidebar.multiselect('Filter By Bathrooms', options=data['bathrooms'].unique())
bathrooms = data['bathrooms'].unique() if bathrooms == [] else bathrooms

city = st.sidebar.multiselect('Filter By City', options=data['city'].unique())
city = data['city'].unique() if city == [] else city

compound = st.sidebar.multiselect('Filter By Compound', options=data['compound'].unique())
compound = data['compound'].unique() if compound == [] else compound

year = st.sidebar.multiselect('Filter By Year Delivery Date', options=data['year'].unique())
year = data['year'].unique() if year == [] else year




df = data[(data['type'].isin(typee)) & (data['bedrooms_num'].isin(bedrooms_num)) & (data['bathrooms'].isin(bathrooms)) & (data['city'].isin(city)) & (data['compound'].isin(compound)) & (data['year'].isin(year)) ]


# ----------------------------
# TAB DEFINITIONS
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Data Overview",
    "Type",
    "Location",
    "Delivery Date"
])


# --------------------------------------------------
# TAB 1 — Overview / KPIs
# --------------------------------------------------
with tab1:
    st.title("Data Overview")
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
    # ========================= KPIs Section =========================
    total_listings = df.shape[0]
    avg_price = df['price'].mean()
    avg_price_per_sqm = df['price_per_sqm'].mean()
    avg_size = df['size_sqm'].mean()
    num_cities = df['city'].nunique()
    num_compounds = df['compound'].nunique()

    left_space, col1, col2, col3, col4, col5, col6, right_space = st.columns([1, 2, 2, 2, 2, 2, 2, 1])

    with col1:
        st.metric("Total Listings", format_number(total_listings))

    with col2:
        st.metric("Average Price", format_number(avg_price))

    with col3:
        st.metric("Average Price per sqm", format_number(avg_price_per_sqm))

    with col4:
        st.metric("Average Size", format_number(avg_size))

    with col5:
        st.metric("Number of Cities", format_number(num_cities))

    with col6:
        st.metric("Number of Compounds", format_number(num_compounds))

    # مسافة بسيطة بعد الـ KPIs
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
    # ========================= CHART PLACEHOLDERS =========================
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader('Average price per type')
        tbl=df.groupby(['type'])['price_per_sqm'].mean().reset_index()
        st.plotly_chart(
        px.bar(tbl, x="type", y='price_per_sqm')
        )

    with col_b:
        st.subheader('Average price per compound (Top 10)')
        tbl=df.groupby(['compound'])['price_per_sqm'].mean().reset_index().head(10)
        st.plotly_chart(
        px.bar(tbl, x="compound", y='price_per_sqm')
        )

    st.subheader('Average price per city')
    st.plotly_chart(
        px.bar(
            df,
            x="city",
            y="price_per_sqm",
            opacity=0.6,
        ).update_xaxes(tickangle=45)

    )

    st.subheader('Room Ratio vs Price')
    df['room_ratio'] = df['bedrooms_num'] / df['bathrooms']
    st.plotly_chart(
    px.scatter(
        df,
        x="room_ratio",
        y="price",
        size="size_sqm",
        color="type",
        labels={"room_ratio": "Room Ratio", "price": "Price"},
        hover_data=["bedrooms_num", "bathrooms", "size_sqm", "type"],
        ))




# --------------------------------------------------
# TAB 2 — Type Analysis
# --------------------------------------------------
with tab2:
    st.title("Type Analysis")
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Average Price per sqm by Unit Type and Maid Availability')
        tbl=df.groupby(["type",'maid'])["price_per_sqm"].mean().reset_index()
        tbl['maid']=tbl['maid'].apply(lambda x: "Yes" if x == 1 else 'No')
        st.plotly_chart(
            px.bar(tbl,
                x="type", y="price_per_sqm",color='maid',barmode='group',
                text_auto=True).update_xaxes(tickangle=45)
        )
    with col2:
        st.subheader('Average size sqm by Unit Type and Maid Availability')
        tbl=df.groupby(["type",'maid'])["size_sqm"].mean().reset_index()
        tbl['maid']=tbl['maid'].apply(lambda x: "Yes" if x == 1 else 'No')
        st.plotly_chart(
            px.bar(
                tbl,x='type',
                y='size_sqm',
                color='maid',
                barmode='group',
                text_auto=True
                ).update_xaxes(tickangle=45)
        )

    col3, col4 = st.columns(2)
    with col3:
        st.subheader('Delivery Units Supply Trend per Year')
        tbl = df.groupby(['year','type']).size().reset_index(name="Number of units")
        st.plotly_chart(
            px.scatter(
                tbl,
                x="type",
                y="year",
                size="Number of units",
                color="year",
                text="Number of units",
                title="Delivery Units Supply Trend per Year",
                size_max=60
            )
        )
    with col4:
        st.subheader('Unit Type Distribution')
        st.plotly_chart(
            px.pie(df, names="type",
            height=500,width=1000)
        )


# --------------------------------------------------
# TAB 3 — Location Analysis
# --------------------------------------------------
with tab3:
    st.title("Location Analysis")

    # ---------------------------------------------------------
    # 1) أعلى 10 مدن حسب متوسط سعر المتر
    # ---------------------------------------------------------
    top_cities = (
        df.groupby("city")["price_per_sqm"]
        .mean()
        .reset_index()
        .sort_values(by="price_per_sqm", ascending=False)
        .head(10)
    )

    top_city_list = top_cities["city"].tolist()


    # ---------------------------------------------------------
    # 2) فلترة الداتا على المدن العشرة فقط
    # ---------------------------------------------------------
    df_filtered = df[df["city"].isin(top_city_list)]


    # ---------------------------------------------------------
    # 3) حساب متوسط سعر المتر لكل كومباوند داخل كل مدينة
    # ---------------------------------------------------------
    compound_tbl = (
        df_filtered.groupby(["city", "compound"])["price_per_sqm"]
        .mean()
        .reset_index()
        .sort_values(by="price_per_sqm", ascending=False)
    )


    # ---------------------------------------------------------
    # 4) أخذ أول 10 كومباوندات داخل كل مدينة
    # ---------------------------------------------------------
    top_10_compounds_per_city = (
        compound_tbl.groupby("city")
        .head(10)
        .reset_index(drop=True)
    )
    st.plotly_chart(
        px.treemap(
            top_10_compounds_per_city,
            path=["city", "compound"],
            values="price_per_sqm",
            color="price_per_sqm",
            title="Top 10 Compounds Within Top 10 Cities (By Avg Price per SQM)",
            color_continuous_scale="Viridis"
            )
        )

    cc1, cc2 = st.columns(2)
    with cc1:
        city_stats = (
        df.groupby("city")
        .agg(
            avg_price_per_sqm=('price_per_sqm','mean'),
            supply=('city','size')
        )
        .reset_index()
        )

        top10 = city_stats.sort_values(by="avg_price_per_sqm", ascending=False).head(10)
        top10["category"] = "Top Cities"

        bottom10 = city_stats.sort_values(by="avg_price_per_sqm", ascending=True).head(10)
        bottom10["category"] = "Bottom Cities"

        combined = pd.concat([top10, bottom10], axis=0)
        st.subheader('Top 10 & Bottom 10 Cities by Avg Price per SQM (with Supply)')
        st.plotly_chart(
            px.sunburst(
                combined,
                path=["category", "city"],
                values="avg_price_per_sqm",
                color="supply",
                color_continuous_scale="Viridis"
                )
        )
    with cc2:
        st.subheader('Top Cities by Average price per sqm and supply')
        tbl = df.groupby("city").size().reset_index(name="supply")
        price_tbl = df.groupby("city")["price_per_sqm"].mean().reset_index(name="avg_price_per_sqm")
        final = tbl.merge(price_tbl, on="city")
        final = final.sort_values(by="supply", ascending=False)
        st.plotly_chart(
            px.bar(
                final.sort_values(by="supply", ascending=True).tail(10),
                x="supply",
                y="city",
                text="avg_price_per_sqm"
                )
        )

    cc3, cc4 = st.columns(2)
    with cc3:
        city_avg = df.groupby("city")["price_per_sqm"].mean().reset_index()
        top10_cities = city_avg.sort_values(by="price_per_sqm", ascending=False).head(10)
        top10_city_list = top10_cities["city"].tolist()

        pivot_type = df[df["city"].isin(top10_city_list)].pivot_table(
            index="city",
            columns="type",
            values="price_per_sqm",
            aggfunc="mean"
        ).reset_index()

        st.subheader('Average Price per sqm by Unit Type Inside Top 10 Cities')
        st.plotly_chart(
            px.bar(
                pivot_type,
                x="city",
                y=[col for col in pivot_type.columns if col != "city"],
                barmode="group",
            )
        )
    with cc4:
        st.subheader('The 20 largest compound by Average size sqm')
        top_20_compound=df.groupby("compound")["size_sqm"].mean().reset_index().sort_values(by='size_sqm',ascending=False).head(20)

        st.plotly_chart(
            px.bar(
                top_20_compound,
                x='compound',
                y='size_sqm',
                text_auto=True,
                ).update_xaxes(tickangle=45)
        )


# --------------------------------------------------
# TAB 4 — Delivery Date
# --------------------------------------------------
with tab4:
    st.title("Delivery Date")

    df_month = df.groupby(["month_name",'month'])["price_per_sqm"].mean().reset_index()
    df_month_sorted = df_month.sort_values("month")
    st.plotly_chart(
        px.line(
            df_month_sorted,
            x="month_name", y="price_per_sqm",
            title="Monthly Price per SQM Pattern Across All Years"
    ))

    ps1, ps2 = st.columns(2)
    with ps1:
        st.subheader('Delivery Units Supply Trend per Year')
        tbl=df.groupby(['year']).size().reset_index(name="Number of units")

        st.plotly_chart(
            px.bar(
                tbl,
                x="year",
                y="Number of units",
                text_auto=True,
       )
        )
    with ps2:
        st.subheader('Average Unit Size by Delivery Year')
        st.plotly_chart(
            px.line(df.groupby("year")["size_sqm"].mean().reset_index(),
            x="year", y="size_sqm",
            )
        )
