"""
=============================================================================
Supermarket Sales Analysis - Streamlit Interactive Frontend Dashboard
=============================================================================
This application builds an interactive, visual web dashboard using Streamlit
and Plotly.

Features:
- Live communication with Flask REST API (with automatic fallback to local engine)
- Executive KPI Cards (Total Revenue, Orders, Avg Basket Size, Avg Rating)
- Interactive Visualizations:
    * Bar Charts (Branch Performance, Top Products, Member vs Normal Spend)
    * Pie/Donut Charts (Payment Method Distribution, Category Share)
    * Line Charts (Sales Trends over Time)
- Data Cleaning Transparency Report
- Filterable Data Explorer with CSV Download option

Beginner Tip:
Streamlit scripts execute top-to-bottom on every user interaction.
Widgets like 'st.selectbox' or 'st.slider' return their selected values,
allowing the page to react immediately!
"""

import sys
import os
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to sys.path so we can import backend if needed
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.data_analysis import SupermarketAnalytics

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Supermarket Sales Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, modern card UI
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 4px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
    }
    .badge-online { background-color: #dcfce7; color: #15803d; }
    .badge-offline { background-color: #fef3c7; color: #b45309; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# BACKEND API CLIENT WITH GRACEFUL FALLBACK
# ---------------------------------------------------------------------------
API_BASE_URL = "http://127.0.0.1:5000/api"

@st.cache_data(ttl=60)
def check_backend_status():
    """Checks whether the Flask API backend is currently reachable."""
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=1.5)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, None

backend_is_online, backend_info = check_backend_status()

# Initialize direct local analytics engine instance for fallback
@st.cache_resource
def get_local_analytics():
    return SupermarketAnalytics()

local_analytics = get_local_analytics()


def fetch_api(endpoint: str, fallback_func):
    """
    Helper function: Requests data from Flask REST API if online;
    otherwise executes the local pandas function seamlessly.
    """
    if backend_is_online:
        try:
            res = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=2.0)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
    # Seamless fallback to direct analytics engine
    return fallback_func()


# ---------------------------------------------------------------------------
# SIDEBAR CONTROLS & ARCHITECTURE STATUS
# ---------------------------------------------------------------------------
st.sidebar.title("🛒 Control Panel")

# Display Backend Connection Badge
if backend_is_online:
    st.sidebar.markdown(
        '<span class="badge-pill badge-online">● Backend: Flask REST API (Port 5000)</span>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<span class="badge-pill badge-offline">● Backend: Direct Pandas Engine</span>',
        unsafe_allow_html=True
    )
    st.sidebar.caption("💡 Run `run_backend.bat` to launch the Flask REST API server.")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Data Filters")

# Cleaned data source for filter options
full_df = local_analytics.cleaned_df

# Branch filter
all_branches = ["All"] + sorted(list(full_df["Branch"].unique()))
selected_branch = st.sidebar.selectbox("Select Branch:", all_branches)

# Customer type filter
all_cust_types = ["All"] + sorted(list(full_df["Customer Type"].unique()))
selected_cust_type = st.sidebar.selectbox("Customer Type:", all_cust_types)

# Payment method filter
all_payments = ["All"] + sorted(list(full_df["Payment Method"].unique()))
selected_payment = st.sidebar.selectbox("Payment Method:", all_payments)

# Apply filters
filtered_df = full_df.copy()
if selected_branch != "All":
    filtered_df = filtered_df[filtered_df["Branch"] == selected_branch]
if selected_cust_type != "All":
    filtered_df = filtered_df[filtered_df["Customer Type"] == selected_cust_type]
if selected_payment != "All":
    filtered_df = filtered_df[filtered_df["Payment Method"] == selected_payment]

st.sidebar.markdown("---")
st.sidebar.info(
    "**Project Tasks Covered:**\n"
    "1. CSV Load with Pandas\n"
    "2. Data Cleaning & Imputation\n"
    "3. Sales = Qty × Unit Price\n"
    "4. 6 Core Analysis Queries\n"
    "5. Flask REST API Backend\n"
    "6. Streamlit Visual Charts\n"
    "7. Beginner-friendly Comments"
)

# ---------------------------------------------------------------------------
# MAIN DASHBOARD HEADER
# ---------------------------------------------------------------------------
st.title("📊 Supermarket Sales Analysis Dashboard")
st.markdown("End-to-End Data Analytics Pipeline with **Pandas**, **Flask API**, and **Streamlit**")

# ---------------------------------------------------------------------------
# EXECUTIVE KPI SUMMARY CARDS
# ---------------------------------------------------------------------------
kpis = local_analytics.get_kpis() if (selected_branch == "All" and selected_cust_type == "All" and selected_payment == "All") else {
    "total_sales": round(float(filtered_df["Sales"].sum()), 2),
    "total_orders": len(filtered_df),
    "average_order_value": round(float(filtered_df["Sales"].mean()), 2) if len(filtered_df) > 0 else 0.0,
    "average_rating": round(float(filtered_df["Rating"].mean()), 2) if len(filtered_df) > 0 else 0.0,
    "top_branch": filtered_df.groupby("Branch")["Sales"].sum().idxmax() if not filtered_df.empty else "N/A"
}

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">${kpis['total_sales']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Orders</div>
        <div class="metric-value">{kpis['total_orders']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Order Value</div>
        <div class="metric-value">${kpis['average_order_value']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Customer Rating</div>
        <div class="metric-value">⭐ {kpis['average_rating']:.1f} / 10</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top Branch</div>
        <div class="metric-value">{kpis['top_branch']}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------------------------
# DATA CLEANING AUDIT REPORT ACCORDION
# ---------------------------------------------------------------------------
with st.expander("🛠️ View Data Cleaning & Transformation Report (Tasks 1, 2 & 3)", expanded=False):
    report = local_analytics.cleaning_report
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.write(f"**Records Loaded:** `{report.get('total_records_loaded', 500)}`")
        st.write(f"**Records Retained:** `{report.get('total_records_cleaned', 500)}`")
    with col_c2:
        st.write(f"**Duplicates Dropped:** `{report.get('duplicates_removed', 0)}`")
        st.write(f"**Missing Values Handled:** `{report.get('missing_values_imputed', {})}`")
    with col_c3:
        st.write(f"**Calculated Column:** `Sales = Quantity × Unit Price`")
        st.write("**Cleaning Techniques:** Title-casing strings, mean imputation on Rating, mode imputation on Customer Type.")

st.markdown("---")

# ---------------------------------------------------------------------------
# ROW 1: PRODUCT & CATEGORY ANALYSIS (BAR & DONUT CHARTS)
# ---------------------------------------------------------------------------
st.subheader("📦 Product & Category Performance (Tasks 4.1 & 4.3)")

col_row1_left, col_row1_right = st.columns([3, 2])

with col_row1_left:
    # Aggregating top products
    top_products_df = (
        filtered_df.groupby("Product")
        .agg(total_sales=("Sales", "sum"), total_qty=("Quantity", "sum"))
        .reset_index()
        .sort_values(by="total_sales", ascending=True)
        .tail(10)
    )

    fig_products = px.bar(
        top_products_df,
        x="total_sales",
        y="Product",
        orientation="h",
        title="Top 10 Selling Products by Revenue ($)",
        labels={"total_sales": "Total Sales ($)", "Product": "Product Name"},
        color="total_sales",
        color_continuous_scale="Blues",
        text_auto="$,.0f"
    )
    fig_products.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_products, use_container_width=True)

with col_row1_right:
    # Aggregating category sales
    category_df = (
        filtered_df.groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values(by="Sales", ascending=False)
    )

    fig_category = px.pie(
        category_df,
        names="Category",
        values="Sales",
        hole=0.45,
        title="Sales Share by Category (%)",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_category.update_traces(textposition="inside", textinfo="percent+label")
    fig_category.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_category, use_container_width=True)

# Highlight insights
best_product_name = top_products_df.iloc[-1]["Product"] if not top_products_df.empty else "N/A"
best_product_sales = top_products_df.iloc[-1]["total_sales"] if not top_products_df.empty else 0.0
best_cat_name = category_df.iloc[0]["Category"] if not category_df.empty else "N/A"

st.caption(
    f"🏆 **Highest Selling Product:** `{best_product_name}` with **${best_product_sales:,.2f}** in revenue | "
    f"🏷️ **Highest Selling Category:** `{best_cat_name}`"
)

st.markdown("---")

# ---------------------------------------------------------------------------
# ROW 2: BRANCH PERFORMANCE & PAYMENT METHODS (BAR & PIE CHARTS)
# ---------------------------------------------------------------------------
col_row2_left, col_row2_right = st.columns(2)

with col_row2_left:
    st.subheader("🏢 Branch Performance (Task 4.2)")

    branch_df = (
        filtered_df.groupby(["Branch", "City"])
        .agg(total_sales=("Sales", "sum"), avg_rating=("Rating", "mean"))
        .round(2)
        .reset_index()
        .sort_values(by="total_sales", ascending=False)
    )

    fig_branch = px.bar(
        branch_df,
        x="Branch",
        y="total_sales",
        color="Branch",
        title="Total Sales Revenue per Branch ($)",
        labels={"total_sales": "Sales ($)", "Branch": "Supermarket Branch"},
        text_auto="$,.0f",
        hover_data=["City", "avg_rating"],
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_branch.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_branch, use_container_width=True)

    if not branch_df.empty:
        best_b = branch_df.iloc[0]
        st.caption(f"🌟 **Best Performing Branch:** `{best_b['Branch']}` ({best_b['City']}) with **${best_b['total_sales']:,.2f}** total revenue.")

with col_row2_right:
    st.subheader("💳 Popular Payment Methods (Task 4.4)")

    payment_df = (
        filtered_df.groupby("Payment Method")
        .agg(
            transaction_count=("Invoice ID", "count"),
            total_sales=("Sales", "sum")
        )
        .reset_index()
        .sort_values(by="transaction_count", ascending=False)
    )

    fig_payment = px.pie(
        payment_df,
        names="Payment Method",
        values="transaction_count",
        title="Transaction Volume by Payment Method",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_payment.update_traces(textposition="inside", textinfo="percent+label")
    fig_payment.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_payment, use_container_width=True)

    if not payment_df.empty:
        top_pay = payment_df.iloc[0]
        st.caption(f"🔥 **Most Popular Method:** `{top_pay['Payment Method']}` with **{top_pay['transaction_count']}** transactions.")

st.markdown("---")

# ---------------------------------------------------------------------------
# ROW 3: MEMBER VS NORMAL SPENDING & RATINGS (TASKS 4.5 & 4.6)
# ---------------------------------------------------------------------------
col_row3_left, col_row3_right = st.columns(2)

with col_row3_left:
    st.subheader("👥 Member vs Normal Spending (Task 4.5)")

    cust_summary = (
        filtered_df.groupby("Customer Type")
        .agg(
            avg_spending=("Sales", "mean"),
            total_orders=("Invoice ID", "count")
        )
        .round(2)
        .reset_index()
    )

    fig_cust = px.bar(
        cust_summary,
        x="Customer Type",
        y="avg_spending",
        color="Customer Type",
        title="Average Spending per Order: Member vs. Normal ($)",
        labels={"avg_spending": "Average Spend ($)", "Customer Type": "Customer Type"},
        text_auto="$,.2f",
        color_discrete_map={"Member": "#3b82f6", "Normal": "#94a3b8"}
    )
    fig_cust.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_cust, use_container_width=True)

    # Compute difference
    m_val = cust_summary[cust_summary["Customer Type"] == "Member"]["avg_spending"].values
    n_val = cust_summary[cust_summary["Customer Type"] == "Normal"]["avg_spending"].values
    if len(m_val) > 0 and len(n_val) > 0:
        diff_val = m_val[0] - n_val[0]
        direction = "higher" if diff_val >= 0 else "lower"
        st.caption(f"💡 **Finding:** Loyalty Members spend **${abs(diff_val):.2f} {direction}** per transaction compared to Normal shoppers.")

with col_row3_right:
    st.subheader("⭐ Customer Ratings Breakdown (Task 4.6)")

    rating_branch_df = (
        filtered_df.groupby("Branch")["Rating"]
        .mean()
        .round(2)
        .reset_index()
        .sort_values(by="Rating", ascending=False)
    )

    fig_rating = px.bar(
        rating_branch_df,
        x="Branch",
        y="Rating",
        color="Branch",
        title="Average Customer Rating by Branch (Scale: 1 - 10)",
        labels={"Rating": "Avg Rating ⭐", "Branch": "Supermarket Branch"},
        text_auto=".2f",
        range_y=[0, 10],
        color_discrete_sequence=px.colors.qualitative.Pastel2
    )
    fig_rating.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_rating, use_container_width=True)

    overall_avg_rating = filtered_df["Rating"].mean() if not filtered_df.empty else 0.0
    st.caption(f"🎯 **Overall Average Rating:** **{overall_avg_rating:.2f} / 10.0** across all evaluated transactions.")

st.markdown("---")

# ---------------------------------------------------------------------------
# ROW 4: SALES TREND OVER TIME (LINE CHART)
# ---------------------------------------------------------------------------
st.subheader("📈 Sales Trend Over Time (Line Chart)")

if "Date" in filtered_df.columns:
    trend_df = (
        filtered_df.groupby("Date")["Sales"]
        .sum()
        .reset_index()
        .sort_values(by="Date")
    )
    # Add rolling moving average
    trend_df["7-Day Moving Avg"] = trend_df["Sales"].rolling(window=7, min_periods=1).mean().round(2)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_df["Date"],
        y=trend_df["Sales"],
        mode="lines+markers",
        name="Daily Sales ($)",
        line=dict(color="#3b82f6", width=2),
        marker=dict(size=4)
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend_df["Date"],
        y=trend_df["7-Day Moving Avg"],
        mode="lines",
        name="7-Day Moving Avg",
        line=dict(color="#f97316", width=3, dash="dash")
    ))
    fig_trend.update_layout(
        title="Daily Supermarket Sales & 7-Day Moving Average",
        xaxis_title="Transaction Date",
        yaxis_title="Total Sales ($)",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# ROW 5: RAW DATA EXPLORER & CSV DOWNLOAD
# ---------------------------------------------------------------------------
st.subheader("📄 Dataset Explorer & Export")
st.write(f"Showing **{len(filtered_df)}** matching transaction records:")

st.dataframe(
    filtered_df.reset_index(drop=True),
    use_container_width=True,
    height=280
)

# CSV Download button
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="supermarket_sales_cleaned.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    "<center style='color: #94a3b8; font-size: 0.85rem;'>"
    "Supermarket Sales Analysis Project | Built with Python, Pandas, Flask & Streamlit"
    "</center>",
    unsafe_allow_html=True
)
