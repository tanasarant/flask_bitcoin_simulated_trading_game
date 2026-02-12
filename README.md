# BTC Trading Simulator

A Binance Bitcoin trading simulation game built with Flask and TradingView Lightweight Charts.

## Features

- 📈 **Live BTC/USDT Chart**: Real-time 15-minute candlestick chart from Binance
- 💰 **Virtual Wallet**: Start with 100 USDT, trade without real risk
- 🟢🔴 **Buy/Sell Buttons**: Easy trading interface with quick amount selectors
- 📊 **Trade History**: Track all your trades
- 🍪 **Persistent Session**: Your wallet is saved in cookies

## Deployment to Railway.app

### Method 1: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Navigate to project directory and initialize:
   ```bash
   cd trading_simulation
   railway init
   ```

4. Deploy:
   ```bash
   railway up
   ```

### Method 2: Using GitHub Integration

1. Create a new GitHub repository
2. Push this code to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

3. In Railway dashboard:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Python app and deploy

### Method 3: Manual Upload

1. Zip the project folder (without venv if you created one)
2. In Railway dashboard:
   - Click "New Project"
   - Select "Upload"
   - Upload your zip file

## Local Development

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open http://localhost:5000 in your browser

## How to Play

1. Open the app - you'll automatically receive 100 USDT
2. Watch the live BTC price chart
3. Enter an amount and click:
   - 🔴 **BUY** (Red button) to buy BTC with your USDT
   - 🟢 **SELL** (Green button) to sell BTC for USDT
4. Try to increase your total portfolio value!

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: TradingView Lightweight Charts
- **Data**: Binance WebSocket & REST API
- **Deployment**: Railway.app

## File Structure

```
trading_simulation/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── README.md          # This file
└── templates/
    └── index.html     # Main game interface
```

## Notes

- This is a simulation game using virtual money
- Prices are real-time from Binance
- Wallet data persists via browser cookies
- Each browser/device gets its own wallet
