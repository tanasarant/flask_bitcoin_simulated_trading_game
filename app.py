
from flask import Flask, render_template, jsonify, request, make_response
import json
import os
import uuid
from datetime import datetime
from threading import Lock

app = Flask(__name__)

# Configuration
COMMISSION_RATE = 0.001  # 0.1%
MIN_TRADE_USDT = 10.00   # Minimum 10 USDT per trade

# File-based storage for Railway (shared across workers)
DATA_FILE = '/tmp/trading_games.json'
data_lock = Lock()

def load_games():
    """Load games from file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_games(games):
    """Save games to file"""
    with data_lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(games, f)

def get_player_wallet(player_id):
    """Get player wallet from storage"""
    games = load_games()
    return games.get(player_id)

def set_player_wallet(player_id, wallet_data):
    """Save player wallet to storage"""
    games = load_games()
    games[player_id] = wallet_data
    save_games(games)

@app.route('/')
def index():
    player_id = request.cookies.get('player_id')
    wallet = None

    if player_id:
        wallet = get_player_wallet(player_id)

    response = make_response(render_template('index.html'))

    # If no cookie exists or wallet not found, create new player with 100 USDT
    if not player_id or not wallet:
        new_player_id = str(uuid.uuid4())
        new_wallet = {
            'usdt': 100.00,
            'btc': 0.00000000,
            'trades': [],
            'created_at': datetime.now().isoformat()
        }
        set_player_wallet(new_player_id, new_wallet)
        response.set_cookie('player_id', new_player_id, max_age=30*24*60*60)

    return response

@app.route('/api/wallet')
def get_wallet():
    player_id = request.cookies.get('player_id')
    if not player_id:
        return jsonify({'error': 'No player ID found'}), 404

    wallet = get_player_wallet(player_id)
    if not wallet:
        return jsonify({'error': 'No active game found'}), 404

    return jsonify({
        'usdt': round(wallet['usdt'], 2),
        'btc': round(wallet['btc'], 8),
        'trades': wallet['trades']
    })

@app.route('/api/trade', methods=['POST'])
def trade():
    player_id = request.cookies.get('player_id')
    if not player_id:
        return jsonify({'error': 'No player ID found'}), 404

    wallet = get_player_wallet(player_id)
    if not wallet:
        return jsonify({'error': 'No active game found'}), 404

    data = request.get_json()
    action = data.get('action')  # 'buy' or 'sell'
    amount = float(data.get('amount', 0))  # For buy: USDT amount, For sell: BTC amount
    price = float(data.get('price', 0))

    if action not in ['buy', 'sell'] or amount <= 0 or price <= 0:
        return jsonify({'error': 'Invalid trade parameters'}), 400

    if action == 'buy':
        # amount is USDT to spend
        usdt_amount = amount

        # Check minimum trade value
        if usdt_amount < MIN_TRADE_USDT:
            return jsonify({'error': f'Minimum trade is {MIN_TRADE_USDT} USDT'}), 400

        # Check if enough USDT
        if usdt_amount > wallet['usdt']:
            return jsonify({'error': 'Insufficient USDT balance'}), 400

        # Calculate BTC received (fee deducted from received BTC)
        btc_before_fee = usdt_amount / price
        fee_btc = btc_before_fee * COMMISSION_RATE
        btc_received = btc_before_fee - fee_btc

        wallet['usdt'] -= usdt_amount
        wallet['btc'] += btc_received

        trade_record = {
            'action': 'BUY',
            'amount': round(btc_received, 8),
            'price': round(price, 2),
            'spent': round(usdt_amount, 2),
            'fee': round(fee_btc, 8),
            'timestamp': datetime.now().isoformat()
        }

    elif action == 'sell':
        # amount is BTC to sell
        btc_amount = amount

        # Check minimum trade value (10 USDT equivalent)
        usdt_value = btc_amount * price
        if usdt_value < MIN_TRADE_USDT:
            return jsonify({'error': f'Minimum trade is {MIN_TRADE_USDT} USDT equivalent'}), 400

        # Check if enough BTC
        if btc_amount > wallet['btc']:
            return jsonify({'error': 'Insufficient BTC balance'}), 400

        # Calculate USDT received (fee deducted from received USDT)
        usdt_before_fee = btc_amount * price
        fee_usdt = usdt_before_fee * COMMISSION_RATE
        usdt_received = usdt_before_fee - fee_usdt

        wallet['btc'] -= btc_amount
        wallet['usdt'] += usdt_received

        trade_record = {
            'action': 'SELL',
            'amount': round(btc_amount, 8),
            'price': round(price, 2),
            'received': round(usdt_received, 2),
            'fee': round(fee_usdt, 2),
            'timestamp': datetime.now().isoformat()
        }

    wallet['trades'].insert(0, trade_record)
    set_player_wallet(player_id, wallet)

    return jsonify({
        'success': True,
        'usdt': round(wallet['usdt'], 2),
        'btc': round(wallet['btc'], 8),
        'trade': trade_record
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    player_id = request.cookies.get('player_id')
    if player_id:
        new_wallet = {
            'usdt': 100.00,
            'btc': 0.00000000,
            'trades': [],
            'created_at': datetime.now().isoformat()
        }
        set_player_wallet(player_id, new_wallet)
    return jsonify({'success': True, 'message': 'Game reset successfully'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
