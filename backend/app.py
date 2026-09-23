"""
=============================================================================
Supermarket Sales Analysis - Flask REST API Backend
=============================================================================
This file sets up a lightweight Flask web server that serves analytical
endpoints in standard JSON format.

Endpoints:
- GET /api/health                    : Check backend server status
- GET /api/cleaning-report           : Details on data cleaning actions
- GET /api/overview                  : KPI metrics (Sales, Orders, Rating, etc.)
- GET /api/analysis/highest-selling-product : Top products by revenue and volume
- GET /api/analysis/branch-performance      : Performance metrics by branch
- GET /api/analysis/category-sales          : Sales distribution across categories
- GET /api/analysis/payment-methods         : Popularity of payment methods
- GET /api/analysis/customer-spending       : Member vs Normal spending comparison
- GET /api/analysis/rating-summary          : Overall & segmented ratings
- GET /api/analysis/sales-trends            : Time-series sales data for line charts
- GET /api/data                             : Paginated / filtered records table

Beginner Note:
Flask uses route decorators like '@app.route("/path")' to bind a URL endpoint
to a Python function. The function returns a JSON response via 'jsonify()'.
"""

import os
import sys

# Ensure parent directory is in sys.path so backend package can be imported reliably
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.data_analysis import SupermarketAnalytics

# Initialize Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so frontend applications
# (like Streamlit running on port 8501 or React) can request data from this API
CORS(app)

# Initialize the analytics engine (loads, cleans, and computes metrics from CSV)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "supermarket_sales.csv")

try:
    analytics = SupermarketAnalytics(csv_path=DATA_FILE)
    print("SupermarketAnalytics initialized successfully.")
except Exception as e:
    analytics = None
    print(f"Warning: Could not initialize analytics on startup ({e}). Generate dataset first.")


# ---------------------------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify backend server is alive and functioning.
    """
    return jsonify({
        "status": "healthy",
        "service": "Supermarket Sales Analysis API",
        "dataset_loaded": analytics is not None and analytics.cleaned_df is not None,
        "total_records": len(analytics.cleaned_df) if analytics and analytics.cleaned_df is not None else 0
    }), 200


@app.route("/api/cleaning-report", methods=["GET"])
def get_cleaning_report():
    """
    Returns audit details of data cleaning operations performed on the dataset.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.cleaning_report), 200


@app.route("/api/overview", methods=["GET"])
def get_overview():
    """
    Returns executive high-level KPI cards:
    Total Revenue, Total Orders, Average Order Value, Average Rating, Top Branch.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_kpis()), 200


@app.route("/api/analysis/highest-selling-product", methods=["GET"])
def highest_selling_product():
    """
    Task 4.1: Returns the highest selling product by revenue & volume,
    plus top N products list. Query param '?limit=5' is supported.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    limit = request.args.get("limit", default=5, type=int)
    return jsonify(analytics.get_highest_selling_product(top_n=limit)), 200


@app.route("/api/analysis/branch-performance", methods=["GET"])
def branch_performance():
    """
    Task 4.2: Returns sales performance and ratings across all supermarket branches.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_best_performing_branch()), 200


@app.route("/api/analysis/category-sales", methods=["GET"])
def category_sales():
    """
    Task 4.3: Returns sales and unit volume broken down by product category.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_highest_selling_category()), 200


@app.route("/api/analysis/payment-methods", methods=["GET"])
def payment_methods():
    """
    Task 4.4: Returns popularity and volume breakdown across payment methods.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_popular_payment_methods()), 200


@app.route("/api/analysis/customer-spending", methods=["GET"])
def customer_spending():
    """
    Task 4.5: Returns spending comparison between Member and Normal customers.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_member_vs_normal_spending()), 200


@app.route("/api/analysis/rating-summary", methods=["GET"])
def rating_summary():
    """
    Task 4.6: Returns overall customer rating and ratings grouped by branch/category.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_average_ratings()), 200


@app.route("/api/analysis/sales-trends", methods=["GET"])
def sales_trends():
    """
    Returns time-series daily sales and moving averages for line charts.
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    return jsonify(analytics.get_sales_trends()), 200


@app.route("/api/data", methods=["GET"])
def get_data():
    """
    Returns raw or filtered transaction records for data table exploration.
    Supports filters:
      - ?branch=Branch+A
      - ?customer_type=Member
      - ?payment=Cash
      - ?limit=100
    """
    if analytics is None:
        return jsonify({"error": "Dataset not loaded"}), 500

    branch = request.args.get("branch", default=None)
    customer_type = request.args.get("customer_type", default=None)
    payment = request.args.get("payment", default=None)
    limit = request.args.get("limit", default=100, type=int)

    filtered_df = analytics.get_filtered_data(
        branch=branch,
        customer_type=customer_type,
        payment=payment
    )

    # Format date column as string for clean JSON serialization
    display_df = filtered_df.copy()
    if "Date" in display_df.columns:
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

    records = display_df.head(limit).to_dict(orient="records")
    return jsonify({
        "total_matches": len(filtered_df),
        "limit": limit,
        "records": records
    }), 200


# ---------------------------------------------------------------------------
# GLOBAL ERROR HANDLERS
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error", "status": 500}), 500


# Run standalone server when executed directly
if __name__ == "__main__":
    # Runs on localhost:5000 in debug mode
    print("Starting Flask API server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
