#!/usr/bin/python3
from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

@app.route("/")
def rest_service():
    temp_query = request.args.get("queryAirportTemp")
    stock_query = request.args.get("queryStockPrice")
    eval_query = request.args.get("queryEval")

    accept = request.headers.get("Accept", "application/json")

    result = None

    if temp_query:
        result = get_airport_temperature(temp_query)
    elif stock_query:
        result = get_stock_price(stock_query)
    elif eval_query:
        result = evaluate_expression(eval_query)
    else:
        return "Bad request: No valid query parameter found", 400

    if accept == "application/xml" or accept == "text/xml":
        return Response(f"<result>{result}</result>", mimetype="application/xml")
    else:
        return jsonify(result)


ACCU_API_KEY = 'dOY9RYElh7zG8DfwMYdmZ1EuddSIxovb'  # Replace with your actual API key
def get_airport_temperature(iata_code):
    # Step 1: Find the location key by searching the POI
    search_url = 'http://dataservice.accuweather.com/locations/v1/poi/search'
    search_params = {
        'apikey': ACCU_API_KEY,
        'q': iata_code
    }
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()

    if not search_data:
        raise ValueError(f"No airport found with IATA code '{iata_code}'")

    location_key = search_data[0]['Key']

    # Step 2: Get current conditions using the location key
    weather_url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    weather_params = {
        'apikey': ACCU_API_KEY
    }
    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    if not weather_data:
        raise ValueError(f"No weather data available for location key '{location_key}'")

    return weather_data[0]['Temperature']['Metric']['Value']



def get_stock_price(symbol):
    # Using
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=IFKW7DXBYSUNW8PM'
    r = requests.get(url)
    data = r.json()

    try:
        time_series = data["Monthly Adjusted Time Series"]
        latest_date = sorted(time_series.keys())[-1]  # oldest → newest, so last is most recent
        latest_data = time_series[latest_date]
        latest_price = latest_data["4. close"]  # Or use "5. adjusted close" if you prefer
        return float(latest_price)
    except KeyError as e:
        return f"Missing key in API response: {e}"
    except Exception as e:
        return f"Error fetching stock price: {e}"

def evaluate_expression(expr):
    try:
        """
        In quaries the + sign is evaluated to space, thats
        why we change it back
        """
        expr = expr.replace(' ', '+')
        return eval(expr, {"__builtins__": None}, {})
    except:
        return "Invalid expression"
if __name__ == "__main__":
    app.run(debug=True)

