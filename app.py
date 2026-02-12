
from flask import Flask, render_template, jsonify, request, make_response
import json
import random
from datetime import datetime

app = Flask(__name__)

# In-memory storage for active games (in production, use Redis or database)
active_games = {}

@app.route('/')
def index():
    # Check if player has existing wallet cookie
    player_id = request.cookies.get('player_id')

    response = make_response(render_template('index.html'))

    # If no cookie exists, create new player with 100 USDT
    if not player_id or player_id not in active_games:
        import uuid
        new_player_id = str(uuid.uuid4())
        active_games[new_player_id] = {
            'usdt': 100.00,
            'btc': 0.00000000,
            'trades': [],
            'created_at': datetime.now().isoformat()
        }
        response.set_cookie('player_id', new_player_id, max_age=30*24*60*60)  # 30 days

    return response

@app.route('/api/wallet')
def get_wallet():
    player_id = request.cookies.get('player_id')
    if not player_id or player_id not in active_games:
        return jsonify({'error': 'No active game found'}), 404

    wallet = active_games[player_id]
    return jsonify({
        'usdt': round(wallet['usdt'], 2),
        'btc': round(wallet['btc'], 8),
        'trades': wallet['trades']
    })

@app.route('/api/trade', methods=['POST'])
def trade():
    player_id = request.cookies.get('player_id')
    if not player_id or player_id not in active_games:
        return jsonify({'error': 'No active game found'}), 404

    data = request.get_json()
    action = data.get('action')  # 'buy' or 'sell'
    amount = float(data.get('amount', 0))
    price = float(data.get('price', 0))

    if action not in ['buy', 'sell'] or amount <= 0 or price <= 0:
        return jsonify({'error': 'Invalid trade parameters'}), 400

    wallet = active_games[player_id]

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

    return jsonify({
        'success': True,
        'usdt': round(wallet['usdt'], 2),
        'btc': round(wallet['btc'], 8),
        'trade': trade_record
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    player_id = request.cookies.get('player_id')
    if player_id and player_id in active_games:
        active_games[player_id] = {
            'usdt': 100.00,
            'btc': 0.00000000,
            'trades': [],
            'created_at': datetime.now().isoformat()
        }
    return jsonify({'success': True, 'message': 'Game reset successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
