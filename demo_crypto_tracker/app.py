from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crypto')
def get_crypto_prices():
    """Get live crypto prices from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,cardano,solana,dogecoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        cryptos = []
        for coin_id, info in data.items():
            cryptos.append({
                "id": coin_id,
                "name": coin_id.title(),
                "price": info.get("usd", 0),
                "change_24h": round(info.get("usd_24h_change", 0), 2)
            })
        
        return jsonify({
            "success": True,
            "cryptos": cryptos,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
