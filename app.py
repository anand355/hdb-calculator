# app.py
# This is your web server — it listens for requests from the browser
# and sends back data from your HDB calculator logic

from flask import Flask, jsonify, request, render_template
import csv
import os

# Create the Flask app — think of this as "turning on" your web server
app = Flask(__name__)


# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────

def load_data():
    records = []
    filepath = "data/ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv"

    if not os.path.exists(filepath):
        return []

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return records

# Load data once when the server starts
ALL_RECORDS = load_data()


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

# Route 1: Home page
@app.route("/")
def home():
    return render_template("index.html")


# Route 2: Search
@app.route("/api/search")
def search():
    town      = request.args.get("town", "").strip().upper() or None
    flat_type = request.args.get("flat_type", "").strip().upper() or None
    year      = request.args.get("year", "").strip() or None

    results = []
    for record in ALL_RECORDS:
        if town and record["town"].upper() != town:
            continue
        if flat_type and record["flat_type"].upper() != flat_type:
            continue
        if year and not record["month"].startswith(year):
            continue
        results.append(record)

    if results:
        prices = [int(r["resale_price"]) for r in results]
        stats = {
            "count":   len(prices),
            "average": sum(prices) // len(prices),
            "minimum": min(prices),
            "maximum": max(prices),
        }
    else:
        stats = None

    return jsonify({
        "results": results[:50],
        "stats":   stats,
        "total":   len(results)
    })


# Route 3: Get all towns
@app.route("/api/towns")
def get_towns():
    towns = sorted(set(r["town"] for r in ALL_RECORDS))
    return jsonify(towns)


# Route 4: Get all flat types
@app.route("/api/flat_types")
def get_flat_types():
    flat_types = sorted(set(r["flat_type"] for r in ALL_RECORDS))
    return jsonify(flat_types)


# Route 5: Price trend by year
@app.route("/api/trend")
def get_trend():
    town      = request.args.get("town", "").strip().upper() or None
    flat_type = request.args.get("flat_type", "").strip().upper() or None

    year_prices = {}
    for record in ALL_RECORDS:
        if town and record["town"].upper() != town:
            continue
        if flat_type and record["flat_type"].upper() != flat_type:
            continue

        year = record["month"][:4]
        price = int(record["resale_price"])

        if year not in year_prices:
            year_prices[year] = []
        year_prices[year].append(price)

    trend = []
    for year in sorted(year_prices.keys()):
        prices = year_prices[year]
        trend.append({
            "year":    year,
            "average": sum(prices) // len(prices),
            "count":   len(prices)
        })

    return jsonify(trend)


# ──────────────────────────────────────────────
# START THE SERVER
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting HDB Calculator web server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True)