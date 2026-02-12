
from flask import Flask, render_template, jsonify, request, make_response
import json
import os
import uuid
from datetime import datetime
from threading import Lock

app = Flask(__name__)

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

def delete_player(player_id):
    """Delete player from storage"""
    games = load_games()
    if player_id in games:
        del games[player_id]
        save_games(games)

@app.route('/')
def index():
    # Check if player has existing wallet cookie
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
        response.set_cookie('player_id', new_player_id, max_age=30*24*60*60)  # 30 days
        print(f"Created new player: {new_player_id}")

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
    amount = float(data.get('amount', 0))
    price = float(data.get('price', 0))

    if action not in ['buy', 'sell'] or amount <= 0 or price <= 0:
        return jsonify({'error': 'Invalid trade parameters'}), 400

    if action == 'buy':
        # Check if enough USDT
        cost = amount * price
        if cost > wallet['usdt']:
            return jsonify({'error': 'Insufficient USDT balance'}), 400

        wallet['usdt'] -= cost
        wallet['btc'] += amount

    elif action == 'sell':
        # Check if enough BTC
        if amount > wallet['btc']:
            return jsonify({'error': 'Insufficient BTC balance'}), 400

        revenue = amount * price
        wallet['usdt'] += revenue
        wallet['btc'] -= amount

    # Record trade
    trade_record = {
        'action': action.upper(),
        'amount': round(amount, 8),
        'price': round(price, 2),
        'total': round(amount * price, 2),
        'timestamp': datetime.now().isoformat()
    }
    wallet['trades'].insert(0, trade_record)  # Add to beginning

    # Save updated wallet
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

# Health check endpoint for Railway
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
