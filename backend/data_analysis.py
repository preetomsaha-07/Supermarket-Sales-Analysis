"""
=============================================================================
Supermarket Sales Analysis - Data Analytics & Cleaning Engine
=============================================================================
This module handles all core data processing tasks:
1. Loading the raw supermarket sales dataset from CSV using pandas.
2. Data cleaning: inspecting and handling missing, duplicate, or malformed data.
3. Feature Engineering: Creating the 'Sales' column (Sales = Quantity * Unit Price).
4. Analytical tasks:
   - Highest selling product (by revenue & volume)
   - Best performing branch (by total sales)
   - Highest selling category
   - Most popular payment method
   - Average spending comparison: Member vs Normal customers
   - Average customer ratings (overall and by branch/category)
   - Time-series sales trend for line charts

All functions are annotated with detailed, beginner-friendly explanations!
"""

import os
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


class SupermarketAnalytics:
    """
    Main analytics class that encapsulates data loading, data cleaning,
    and business metric calculations.
    """

    def __init__(self, csv_path: str = "data/supermarket_sales.csv"):
        """
        Initializes the analytics engine with the path to the CSV file.
        Automatically loads and cleans the dataset upon instantiation.
        """
        self.csv_path = csv_path
        self.raw_df = None
        self.cleaned_df = None
        self.cleaning_report = {}
        self.load_and_clean_data()

    def load_and_clean_data(self) -> pd.DataFrame:
        """
        Step 1 & 2 & 3:
        - Loads CSV using pandas.read_csv()
        - Audits missing values, duplicates, and invalid data types
        - Cleans and repairs data
        - Calculates the 'Sales' column = Quantity * Unit Price
        """
        # Resolve absolute path to handle execution from any directory
        if not os.path.isabs(self.csv_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resolved_path = os.path.join(base_dir, self.csv_path)
        else:
            resolved_path = self.csv_path

        if not os.path.exists(resolved_path):
            raise FileNotFoundError(
                f"Dataset not found at '{resolved_path}'. "
                f"Please run 'python scripts/generate_data.py' first."
            )

        # -------------------------------------------------------------
        # STEP 1: Load the CSV dataset into a pandas DataFrame
        # -------------------------------------------------------------
        # A DataFrame is essentially an in-memory 2D table (like an Excel sheet)
        df = pd.read_csv(resolved_path)
        self.raw_df = df.copy()

        # -------------------------------------------------------------
        # STEP 2: Clean the Data
        # -------------------------------------------------------------
        # 2a. Record initial missing counts for beginner visibility
        missing_before = df.isnull().sum().to_dict()
        duplicates_count = int(df.duplicated(subset=["Invoice ID"]).sum())

        # 2b. Standardize text columns (remove extra spaces and normalize casing)
        if "Branch" in df.columns:
            df["Branch"] = df["Branch"].astype(str).str.title().str.strip()
            # Standardize and synchronize City according to supermarket Branch location
            branch_city_map = {
                "Branch A": "Yangon",
                "Branch B": "Mandalay",
                "Branch C": "Naypyitaw"
            }
            # Fill or correct City if mapped branch exists
            df["City"] = df["Branch"].map(branch_city_map).fillna(df.get("City", "Unknown"))

        if "Customer Type" in df.columns:
            # If Customer Type has missing values, impute with the most frequent value (Mode)
            mode_customer = df["Customer Type"].mode()[0] if not df["Customer Type"].dropna().empty else "Normal"
            df["Customer Type"] = df["Customer Type"].fillna(mode_customer).str.capitalize().str.strip()

        if "Payment Method" in df.columns:
            df["Payment Method"] = df["Payment Method"].astype(str).str.strip()

        # 2c. Validate and clean numeric columns
        # Ensure Quantity is numeric and integer
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(1).astype(int)

        # Ensure Unit Price is positive float
        df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0.0).astype(float)

        # Impute missing Rating values with the overall mean rating
        if "Rating" in df.columns:
            df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
            mean_rating = round(float(df["Rating"].mean()), 2)
            df["Rating"] = df["Rating"].fillna(mean_rating)

        # Remove duplicate records if any exist based on Invoice ID
        df = df.drop_duplicates(subset=["Invoice ID"], keep="first").reset_index(drop=True)

        # Parse Date column to datetime for proper time-series sorting
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.sort_values(by="Date").reset_index(drop=True)

        # -------------------------------------------------------------
        # STEP 3: Create the 'Sales' Column
        # Task requirement: Sales = Quantity * Unit Price
        # -------------------------------------------------------------
        # Vectorized multiplication is blazing fast and standard in pandas
        df["Sales"] = (df["Quantity"] * df["Unit Price"]).round(2)

        self.cleaned_df = df

        # Summary of cleaning actions performed
        self.cleaning_report = {
            "total_records_loaded": int(len(self.raw_df)),
            "total_records_cleaned": int(len(self.cleaned_df)),
            "duplicates_removed": duplicates_count,
            "missing_values_imputed": {k: int(v) for k, v in missing_before.items() if v > 0},
            "new_columns_added": ["Sales"]
        }

        return self.cleaned_df

    def get_kpis(self) -> Dict[str, Any]:
        """
        Calculates executive summary KPI cards:
        - Total Sales Revenue ($)
        - Total Transactions
        - Average Order Value ($)
        - Overall Average Customer Rating
        - Best Selling Branch
        """
        df = self.cleaned_df
        total_sales = float(df["Sales"].sum())
        total_orders = int(len(df))
        avg_order_value = float(df["Sales"].mean()) if total_orders > 0 else 0.0
        avg_rating = float(df["Rating"].mean()) if "Rating" in df.columns else 0.0

        # Branch with highest sales
        top_branch = df.groupby("Branch")["Sales"].sum().idxmax()

        return {
            "total_sales": round(total_sales, 2),
            "total_orders": total_orders,
            "average_order_value": round(avg_order_value, 2),
            "average_rating": round(avg_rating, 2),
            "top_branch": str(top_branch)
        }

    # -----------------------------------------------------------------
    # STEP 4: ANALYTICAL FUNCTIONS
    # -----------------------------------------------------------------

    def get_highest_selling_product(self, top_n: int = 5) -> Dict[str, Any]:
        """
        Task 4.1: Identify the highest selling product.
        Analyzes products by both:
        - Total Sales Revenue ($)
        - Total Quantity Sold (Units)
        """
        df = self.cleaned_df

        # Group by product name and aggregate both Sales and Quantity
        product_summary = (
            df.groupby("Product")
            .agg(
                total_sales=("Sales", "sum"),
                total_quantity=("Quantity", "sum"),
                avg_unit_price=("Unit Price", "mean"),
                order_count=("Invoice ID", "count")
            )
            .round(2)
            .reset_index()
        )

        # Sort descending by total_sales
        by_sales = product_summary.sort_values(by="total_sales", ascending=False)
        top_by_sales = by_sales.iloc[0].to_dict()

        # Sort descending by total_quantity
        by_qty = product_summary.sort_values(by="total_quantity", ascending=False)
        top_by_qty = by_qty.iloc[0].to_dict()

        return {
            "highest_by_sales": top_by_sales,
            "highest_by_quantity": top_by_qty,
            "top_products_list": by_sales.head(top_n).to_dict(orient="records")
        }

    def get_best_performing_branch(self) -> Dict[str, Any]:
        """
        Task 4.2: Identify the best performing branch.
        Computes total sales, order count, and average rating per branch.
        """
        df = self.cleaned_df

        branch_summary = (
            df.groupby(["Branch", "City"])
            .agg(
                total_sales=("Sales", "sum"),
                order_count=("Invoice ID", "count"),
                avg_rating=("Rating", "mean"),
                avg_sales_per_order=("Sales", "mean")
            )
            .round(2)
            .reset_index()
            .sort_values(by="total_sales", ascending=False)
        )

        best_branch = branch_summary.iloc[0].to_dict()

        return {
            "best_branch": best_branch,
            "all_branches": branch_summary.to_dict(orient="records")
        }

    def get_highest_selling_category(self) -> Dict[str, Any]:
        """
        Task 4.3: Identify the highest selling category.
        Ranks product lines/categories by total revenue.
        """
        df = self.cleaned_df

        category_summary = (
            df.groupby("Category")
            .agg(
                total_sales=("Sales", "sum"),
                total_units=("Quantity", "sum"),
                order_count=("Invoice ID", "count")
            )
            .round(2)
            .reset_index()
            .sort_values(by="total_sales", ascending=False)
        )

        top_category = category_summary.iloc[0].to_dict()

        return {
            "highest_category": top_category,
            "all_categories": category_summary.to_dict(orient="records")
        }

    def get_popular_payment_methods(self) -> Dict[str, Any]:
        """
        Task 4.4: Find the most popular payment method.
        Calculates transaction count, percentage share, and total sales per method.
        """
        df = self.cleaned_df

        total_transactions = len(df)
        payment_summary = (
            df.groupby("Payment Method")
            .agg(
                transaction_count=("Invoice ID", "count"),
                total_sales=("Sales", "sum"),
                avg_transaction_value=("Sales", "mean")
            )
            .round(2)
            .reset_index()
            .sort_values(by="transaction_count", ascending=False)
        )

        # Calculate percentage share of all transactions
        payment_summary["share_percentage"] = (
            (payment_summary["transaction_count"] / total_transactions) * 100
        ).round(2)

        most_popular = payment_summary.iloc[0].to_dict()

        return {
            "most_popular_method": most_popular,
            "all_methods": payment_summary.to_dict(orient="records")
        }

    def get_member_vs_normal_spending(self) -> Dict[str, Any]:
        """
        Task 4.5: Compare Member vs Normal customer average spending.
        Compares average spending per order, total spending, and transaction count.
        """
        df = self.cleaned_df

        customer_summary = (
            df.groupby("Customer Type")
            .agg(
                avg_spending=("Sales", "mean"),
                total_spending=("Sales", "sum"),
                total_orders=("Invoice ID", "count"),
                avg_rating=("Rating", "mean")
            )
            .round(2)
            .reset_index()
        )

        # Extract specific figures for quick comparison
        member_stats = customer_summary[customer_summary["Customer Type"] == "Member"]
        normal_stats = customer_summary[customer_summary["Customer Type"] == "Normal"]

        member_avg = float(member_stats["avg_spending"].values[0]) if not member_stats.empty else 0.0
        normal_avg = float(normal_stats["avg_spending"].values[0]) if not normal_stats.empty else 0.0
        diff = round(member_avg - normal_avg, 2)
        diff_percent = round((diff / normal_avg) * 100, 2) if normal_avg > 0 else 0.0

        return {
            "member_avg_spend": member_avg,
            "normal_avg_spend": normal_avg,
            "spend_difference": diff,
            "spend_diff_percent": diff_percent,
            "summary_table": customer_summary.to_dict(orient="records")
        }

    def get_average_ratings(self) -> Dict[str, Any]:
        """
        Task 4.6: Calculate average customer rating.
        Computes overall mean rating as well as ratings broken down by Branch and Category.
        """
        df = self.cleaned_df

        overall_avg = round(float(df["Rating"].mean()), 2)

        # Rating by Branch
        branch_ratings = (
            df.groupby("Branch")["Rating"]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={"Rating": "avg_rating"})
            .sort_values(by="avg_rating", ascending=False)
            .to_dict(orient="records")
        )

        # Rating by Category
        category_ratings = (
            df.groupby("Category")["Rating"]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={"Rating": "avg_rating"})
            .sort_values(by="avg_rating", ascending=False)
            .to_dict(orient="records")
        )

        return {
            "overall_average_rating": overall_avg,
            "ratings_by_branch": branch_ratings,
            "ratings_by_category": category_ratings
        }

    def get_sales_trends(self) -> Dict[str, Any]:
        """
        Calculates time-series sales trends for line charts.
        Aggregates daily sales and computes a 7-day rolling moving average.
        """
        df = self.cleaned_df.copy()
        if "Date" not in df.columns:
            return {"daily_sales": []}

        # Format date as YYYY-MM-DD string
        df["DateStr"] = df["Date"].dt.strftime("%Y-%m-%d")

        daily = (
            df.groupby("DateStr")
            .agg(
                daily_sales=("Sales", "sum"),
                order_count=("Invoice ID", "count")
            )
            .round(2)
            .reset_index()
        )

        # Compute 7-period rolling average for smoother trend visualization
        daily["rolling_avg_sales"] = daily["daily_sales"].rolling(window=5, min_periods=1).mean().round(2)

        return {
            "daily_sales": daily.to_dict(orient="records")
        }

    def get_filtered_data(self, branch: str = None, customer_type: str = None, payment: str = None) -> pd.DataFrame:
        """
        Returns a filtered slice of the cleaned DataFrame based on user selections.
        Useful for interactive filtering on the frontend dashboard.
        """
        df = self.cleaned_df.copy()

        if branch and branch != "All":
            df = df[df["Branch"] == branch]
        if customer_type and customer_type != "All":
            df = df[df["Customer Type"] == customer_type]
        if payment and payment != "All":
            df = df[df["Payment Method"] == payment]

        return df


# Quick self-test demonstration
if __name__ == "__main__":
    analytics = SupermarketAnalytics()
    print("=== DATA CLEANING REPORT ===")
    print(analytics.cleaning_report)
    print("\n=== EXECUTIVE KPIS ===")
    print(analytics.get_kpis())
    print("\n=== TOP PRODUCT ===")
    print(analytics.get_highest_selling_product())
    print("\n=== BEST BRANCH ===")
    print(analytics.get_best_performing_branch())
