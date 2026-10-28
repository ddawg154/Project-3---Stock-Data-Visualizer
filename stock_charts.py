
import os
import requests
import pygal
import webbrowser
from datetime import datetime
from pathlib import Path

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

print("Stock Data Chart Generator")
print("--------------------------")

symbol = input("Enter stock symbol: ").strip().upper()

while not symbol:
    symbol = input("Enter a valid stock symbol: ").strip().upper()

while True:
    print("\nChart Types")
    print("-----------")
    print("1. Bar")
    print("2. Line")

    chart_type = input("Enter chart type (1, 2): ")

    if chart_type in ("1", "2"):
        break

    print("Enter a 1 or 2 for chart type.")

while True:
    print("\nSelect the Time Series")
    print("----------------------")
    print("1. Intraday")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")

    time_series = input("Enter time series option (1, 2, 3, 4): ")

    if time_series in ("1", "2", "3", "4"):
        break

    print("Enter a number between 1 and 4.")

functions = {
    "1": ("TIME_SERIES_INTRADAY", "Time Series (5min)"),
    "2": ("TIME_SERIES_DAILY", "Time Series (Daily)"),
    "3": ("TIME_SERIES_WEEKLY", "Weekly Time Series"),
    "4": ("TIME_SERIES_MONTHLY", "Monthly Time Series")
}

while True:
    try:
        start = input("\nEnter start date (YYYY-MM-DD): ")
        end = input("Enter end date (YYYY-MM-DD): ")

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        if start_date > end_date:
            print("Error: Start date cannot be later than End date.")
            continue

        break

    except ValueError:
        print("Invalid date format. Enter the dates again.")

if not API_KEY:
    print("Error: API key not found.")
    raise SystemExit

function, data_key = functions[time_series]

params = {
    "function": function,
    "symbol": symbol,
    "apikey": API_KEY
}

if time_series == "1":
    params["interval"] = "5min"

if time_series == "2":
    params["outputsize"] = "full"

print("\nRetrieving stock data...")

try:
    response = requests.get(
        "https://www.alphavantage.co/query",
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

except (requests.RequestException, ValueError) as error:
    print("Error retrieving data:", error)
    raise SystemExit

if data_key not in data:
    print("API Error:", data.get(
        "Information",
        data.get("Note",
        data.get("Error Message", "No data available."))
    ))
    raise SystemExit

dates = []
open_prices = []
high_prices = []
low_prices = []
close_prices = []

for date, values in data[data_key].items():
    current_date = datetime.strptime(date[:10], "%Y-%m-%d")

    if start_date <= current_date <= end_date:
        dates.append(date)
        open_prices.append(float(values["1. open"]))
        high_prices.append(float(values["2. high"]))
        low_prices.append(float(values["3. low"]))
        close_prices.append(float(values["4. close"]))

if not dates:
    print("No stock data available for the selected date range.")
    raise SystemExit

stock_data = sorted(zip(
    dates, open_prices, high_prices, low_prices, close_prices
))

dates, open_prices, high_prices, low_prices, close_prices = map(
    list, zip(*stock_data)
)

if chart_type == "1":
    chart = pygal.Bar(x_label_rotation=45)
else:
    chart = pygal.Line(x_label_rotation=45, show_dots=True)

chart.title = f"Stock Data for {symbol}: {start} to {end}"
chart.x_labels = dates

chart.add("Open", open_prices)
chart.add("High", high_prices)
chart.add("Low", low_prices)
chart.add("Close", close_prices)

file_path = Path("stock_chart.svg").resolve()

chart.render_to_file(str(file_path))
webbrowser.open(file_path.as_uri())

print("\nChart generated successfully!")
