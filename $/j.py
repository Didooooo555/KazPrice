from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('h.html')

@app.route('/api/rates')
def api_rates():
    try:
        # Новый надёжный источник
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        rates = data.get("rates", {})
        usd_to_kzt = rates.get("KZT")
        usd_to_rub = rates.get("RUB")
        usd_to_cny = rates.get("CNY")

        if not all([usd_to_kzt, usd_to_rub, usd_to_cny]):
            raise ValueError("API не вернул нужные валюты")

        result = {
            "USD": round(usd_to_kzt, 2),
            "RUB": round(usd_to_kzt / usd_to_rub, 2),
            "CNY": round(usd_to_kzt / usd_to_cny, 2)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
