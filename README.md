# 🛒 Supermarket Sales Analysis

An end-to-end Python Data Analytics project featuring:
1. **Pandas Data Pipeline**: Load, audit, clean, and enrich a 500-transaction supermarket dataset.
2. **Flask REST API Backend**: Modular analytics endpoints returning clean JSON responses.
3. **Streamlit Interactive Dashboard**: Visual UI featuring KPI cards, Plotly charts (Bar, Pie, Donut, Line), live filters, and CSV export.

---

## 📁 Project Structure

```text
Preetom Saha_Super Market Sales Analysis/
├── data/
│   └── supermarket_sales.csv       # 500-transaction dataset
├── backend/
│   ├── __init__.py                 # Python package identifier
│   ├── data_analysis.py            # Pandas cleaning & analytical logic (Tasks 1-4)
│   └── app.py                      # Flask REST API server (Task 5)
├── frontend/
│   └── dashboard.py                # Streamlit interactive dashboard (Task 6)
├── scripts/
│   └── generate_data.py            # Synthetic dataset generator
├── requirements.txt                # Python package dependencies
├── run_backend.bat                 # 1-Click launcher for Flask API
├── run_frontend.bat                # 1-Click launcher for Streamlit Dashboard
└── README.md                       # Complete documentation & beginner guide
```

---

## 🎯 Project Requirements & Tasks Addressed

| # | Task | Implementation Location |
|---|------|-------------------------|
| **1** | Load CSV with pandas | `backend/data_analysis.py` -> `SupermarketAnalytics.load_and_clean_data()` |
| **2** | Clean data (missing/incorrect values, casing) | `backend/data_analysis.py` -> Handles nulls (mean/mode), casing, and deduplication |
| **3** | Calculate `Sales = Quantity × Unit Price` | `backend/data_analysis.py` -> Vectorized pandas calculation |
| **4.1** | Highest selling product (Revenue & Volume) | `get_highest_selling_product()` -> Top product identification |
| **4.2** | Best performing branch | `get_best_performing_branch()` -> Ranked branches by revenue |
| **4.3** | Highest selling category | `get_highest_selling_category()` -> Aggregated category sales |
| **4.4** | Most popular payment method | `get_popular_payment_methods()` -> Transaction counts & percentage shares |
| **4.5** | Member vs Normal customer spending | `get_member_vs_normal_spending()` -> Average ticket size comparison |
| **4.6** | Average customer rating | `get_average_ratings()` -> Overall rating & branch breakdown |
| **5** | Flask backend API functions | `backend/app.py` -> 10 REST endpoints with CORS |
| **6** | Frontend Streamlit dashboard | `frontend/dashboard.py` -> Bar, Pie/Donut, and Line charts |
| **7** | Beginner-friendly comments | Documented across all code files |

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.10+ (or Python 3.12 included in `.venv`).

### Step 1: Run the Backend (Flask API)
Double-click `run_backend.bat`, or run from terminal:
```powershell
.venv\Scripts\python backend/app.py
```
Backend API will start at: `http://127.0.0.1:5000`

### Step 2: Run the Frontend (Streamlit Dashboard)
Double-click `run_frontend.bat`, or run from terminal:
```powershell
.venv\Scripts\streamlit run frontend/dashboard.py
```
The interactive dashboard will automatically open in your default browser at:
`http://localhost:8501`

---

## 🌐 Flask REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health status and dataset record count |
| `GET` | `/api/cleaning-report` | Summary of missing values and cleaning steps |
| `GET` | `/api/overview` | Executive KPI metrics (Total sales, orders, avg rating) |
| `GET` | `/api/analysis/highest-selling-product` | Top selling product by revenue and volume |
| `GET` | `/api/analysis/branch-performance` | Performance metrics across supermarket branches |
| `GET` | `/api/analysis/category-sales` | Revenue breakdown by product category |
| `GET` | `/api/analysis/payment-methods` | Popularity distribution of payment methods |
| `GET` | `/api/analysis/customer-spending` | Comparison of Member vs. Normal spending |
| `GET` | `/api/analysis/rating-summary` | Average customer ratings overall and by branch |
| `GET` | `/api/analysis/sales-trends` | Daily sales time-series for line charts |
| `GET` | `/api/data` | Filterable raw transaction table records |

---

## 💡 Key Data Insights Explained for Beginners

1. **Why `Quantity × Unit Price`?**
   - In raw point-of-sale data, line items record unit prices and units sold. Multiplying them vectorially (`df['Quantity'] * df['Unit Price']`) calculates gross line revenue without slow Python loops.
2. **Missing Value Imputation**:
   - Numeric ratings are imputed with the column mean to preserve overall distribution.
   - Categorical fields (like `Customer Type`) are imputed with the statistical mode (most frequent value).
3. **Resilient Frontend Design**:
   - The Streamlit frontend connects directly to the Flask REST API. If the Flask server is ever stopped or not yet started, Streamlit gracefully falls back to the embedded Pandas engine so your dashboard never crashes!
