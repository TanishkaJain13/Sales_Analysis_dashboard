import streamlit as st 
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
import random
import re
import time



st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Sales Dashboard Analysis")




all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Connect to MySQL
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="taani",
        password="Tanishka1234@",
        database="sales_dashboard"
    )
    cursor = conn.cursor()

    # Run query
    cursor.execute("SELECT * FROM financial_data")
    results = cursor.fetchall()
    columns = [i[0] for i in cursor.description]

    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)

    # Display in Streamlit
    with st.expander("Data Preview"):
        st.dataframe(df)

except mysql.connector.Error as err:
    st.error(f"Database connection error: {err}")


def clean_accounting_format(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        # Remove dollar signs and commas
        value = value.replace("$", "").replace(",", "").strip()
        # Convert (number) to -number
        if re.match(r"^\(.*\)$", value):
            value = "-" + value.strip("()")
    try:
        return float(value)
    except:
        return None

# Apply to each month column
for month in all_months:
    if month in df.columns:
        df[month] = df[month].apply(clean_accounting_format)

@st.cache_data
def plot_bottom_left():
    # Wrap each column name in backticks to avoid SQL syntax errors
    month_columns_sql = ','.join([f"`{month}`" for month in all_months])

    query = f"""
        SELECT Scenario, {month_columns_sql}
        FROM financial_data
        WHERE Year = '2023-01-01 00:00:00' AND Account = 'Sales' AND business_unit = 'Software'
    """

    # st.code(query, language='sql')  # Optional: show query in Streamlit

    cursor.execute(query)
    results = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df = pd.DataFrame(results, columns=columns)

    # Melt the DataFrame to long format
    df_melted = df.melt(id_vars='Scenario', value_vars=all_months,
                        var_name='month', value_name='sales')

    df_melted['month'] = pd.Categorical(df_melted['month'], categories=all_months, ordered=True)
    df_melted = df_melted.sort_values(['Scenario', 'month'])

    st.subheader("Sales Trend (2023 - Software)")
    fig = px.line(df_melted, x='month', y='sales', color='Scenario', markers=True)
    st.plotly_chart(fig, use_container_width=True)

# At the end of your script, after all functions:

total_sales = df[(df["Year"] == "2023") & (df["Account"] == "Sales") & (df["business_unit"] == "Software")][all_months].sum(axis=1).sum()



def plot_metric(label="Total Sales 2023", value=total_sales, prefix="$", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 28,
            },
            title={
                "text": label,
                "font": {"size": 20},
                
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={
                    "color": color_graph,
                },
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        margin=dict(t=30, b=0),
        showlegend=False,
        
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)




def plot_gauge(
    indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound
):
    placeholder = st.empty()
    steps = 50
    delay = 0.04  # seconds between updates

    for i in range(steps + 1):
        current_value = (indicator_number / steps) * i

        fig = go.Figure(
            go.Indicator(
                value=current_value,
                mode="gauge+number",
                domain={"x": [0, 1], "y": [0, 1]},
                number={
                    "suffix": indicator_suffix,
                    "font.size": 26,
                },
                gauge={
                    "axis": {"range": [0, max_bound], "tickwidth": 1},
                    "bar": {"color": indicator_color},
                },
                title={
                    "text": indicator_title,
                    "font": {"size": 20}
                },
            )
        )
        fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=50, b=10, pad=8)
        )
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(delay)

def plot_top_right():
    filtered_df = df[(df["Year"] == "2023") & (df["Account"] == "Sales")]
    
    
    # Clean month columns
    for month in all_months:
        if month in df.columns:
            df[month] = pd.to_numeric(df[month], errors='coerce')
    


    df_melted = filtered_df.melt(
        id_vars=["Scenario", "business_unit"],
        value_vars=all_months,
        var_name="month",
        value_name="sales"
    )

    df_melted["sales"] = pd.to_numeric(df_melted["sales"], errors="coerce")

    
    aggregated = df_melted.groupby(["Scenario", "business_unit"])["sales"].sum().reset_index()

    fig = px.bar(
        aggregated,
        x="business_unit",
        y="sales",
        color="Scenario",
        barmode="group",
        title="Sales for Year 2023",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    




top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)

with top_left_column:
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        plot_metric(
            "Total Accounts Receivable",
            6621280,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.6)"
        )
        plot_gauge(1.86, "#0068C9", "%", "Current Ratio", 3)

    with column_2:
        plot_metric(
            "Total Accounts Payable",
            1630270,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(255, 43, 43, 0.4)",
        )
        plot_gauge(10, "#FF8700", " days", "In Stock", 31)

    with column_3:
        plot_metric("Equity Ratio", 75.38, prefix="", suffix=" %", show_graph=False)
        plot_gauge(7, "#FF2B2B", " days", "Stock Out", 31)
        
    with column_4:
        plot_metric("Debt Equity", 1.10, prefix="", suffix=" %", show_graph=False)
        plot_gauge(28, "#29B09D", " days", "Delay", 31)



def plot_bottom_right():
    # Convert Year column to datetime once at the start
    df["Year"] = pd.to_datetime(df["Year"], errors='coerce')

    # Filter data for 2023, Actuals scenario, and non-Sales accounts
    filtered_df = df[
        
        (df["Scenario"] == "Actuals") &
        (df["Account"] != "Sales")
    ]

    # Clean all month columns
    for month in all_months:
        if month in filtered_df.columns:
            filtered_df[month] = filtered_df[month].apply(clean_accounting_format)

    # Melt the DataFrame to unpivot month columns into rows
    df_melted = filtered_df.melt(
        id_vars=["Year", "Account"],
        value_vars=all_months,
        var_name="Month",
        value_name="Sales"
    )

    # Convert sales to numeric
    df_melted["Sales"] = pd.to_numeric(df_melted["Sales"], errors="coerce").abs()

    # Drop rows with null values if any
    df_melted.dropna(subset=["Sales"], inplace=True)

    # Aggregate sales per Account per Year
    aggregated = df_melted.groupby(["Year", "Account"])["Sales"].sum().reset_index()

    # Plot using Plotly
    fig = px.bar(
        aggregated,
        x="Year",
        y="Sales",
        color="Account",
        barmode="stack",
        title="Actual Yearly Sales Per Account (Excluding Sales)"
    )

    fig.update_traces(
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )

    st.plotly_chart(fig, use_container_width=True)




with top_right_column:
    plot_top_right()

with bottom_left_column:
    plot_bottom_left()

with bottom_right_column:
    plot_bottom_right()

# Now close it
if 'conn' in locals() and conn.is_connected():
    cursor.close()
    conn.close()


