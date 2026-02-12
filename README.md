# Stock Analyzer

AI-powered stock analysis with real-time data and ML predictions.

## Features
- Real-time stock data from Yahoo Finance
- Machine Learning price predictions (7-day forecast)
- Technical indicators (RSI, MACD, Moving Averages)
- AI-powered buy/sell signals
- Interactive charts and visualizations

## Tech Stack
- **Backend:** Python, Flask, yfinance, scikit-learn
- **Frontend:** React, Recharts, Tailwind CSS
- **Deployment:** AWS EC2, Nginx, Gunicorn

## Local Development

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend will run on: http://localhost:5000

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend will run on: http://localhost:3000

## API Endpoints
- `GET /api/stock/<ticker>` - Get full stock analysis
- `GET /api/predict/<ticker>/<days>` - Get price predictions (max 30 days)
- `GET /health` - Health check

## Example Usage
```bash
# Get Apple stock data
curl http://localhost:5000/api/stock/AAPL

# Get 14-day prediction for Tesla
curl http://localhost:5000/api/predict/TSLA/14
```

## Deployment
See `deployment/` folder for AWS EC2 deployment scripts.

## Environment Variables
Create `backend/.env` file: