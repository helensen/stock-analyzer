"""
Stock Analyzer with Real-Time Data & ML Predictions
Author: Abel Muanda
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score
import warnings
import os
from stock_utils import find_ticker, search_companies
from symbols import POPULAR_STOCKS

warnings.filterwarnings('ignore')

app = Flask(__name__)

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*"
    }
})

def safe_round(value, decimals=2):
    """Safely round a value, handling None and NaN"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if np.isnan(value) or np.isinf(value):
            return None
        return round(float(value), decimals)
    return None

def safe_float(value, default=0.0):
    """Safely convert to float"""
    if value is None:
        return default
    try:
        result = float(value)
        if np.isnan(result) or np.isinf(result):
            return default
        return result
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    """Safely convert to int"""
    if value is None:
        return default
    try:
        result = int(value)
        return result
    except (TypeError, ValueError):
        return default

class StockAnalyzer:
    """Main class for stock analysis and predictions"""
    
    def __init__(self, ticker):
        self.ticker = str(ticker).upper()
        self.stock = yf.Ticker(self.ticker)
        
    def get_current_data(self):
        """Get current stock information"""
        try:
            info = self.stock.info
            
            # Get current price
            current_price = info.get('currentPrice')
            if current_price is None:
                current_price = info.get('regularMarketPrice')
            if current_price is None:
                current_price = info.get('previousClose')
            
            current_price = safe_float(current_price, 0)
            
            # Get previous close
            previous_close = safe_float(info.get('previousClose'), 0)
            
            if current_price == 0 or previous_close == 0:
                return None
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            # Get other data
            high_52week = safe_float(info.get('fiftyTwoWeekHigh'), current_price)
            low_52week = safe_float(info.get('fiftyTwoWeekLow'), current_price)
            volume = safe_int(info.get('volume'), 0)
            market_cap = safe_int(info.get('marketCap'), 0)
            
            # Get company name
            company_name = info.get('longName')
            if not company_name:
                company_name = info.get('shortName')
            if not company_name:
                company_name = self.ticker
            
            return {
                'symbol': self.ticker,
                'currentPrice': safe_round(current_price, 2),
                'previousClose': safe_round(previous_close, 2),
                'change': safe_round(change, 2),
                'changePercent': safe_round(change_percent, 2),
                'high52Week': safe_round(high_52week, 2),
                'low52Week': safe_round(low_52week, 2),
                'volume': volume,
                'marketCap': market_cap,
                'companyName': str(company_name)
            }
        except Exception as e:
            print(f"Error fetching current data for {self.ticker}: {str(e)}")
            return None
    
    def get_historical_data(self, period='3mo'):
        """Get historical price data with technical indicators"""
        try:
            df = self.stock.history(period=period)
            
            if df.empty:
                print(f"No historical data found for {self.ticker}")
                return []
            
            df = df.reset_index()
            
            # Calculate moving averages
            df['MA7'] = df['Close'].rolling(window=7).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            # Calculate technical indicators
            df['RSI'] = self.calculate_rsi(df['Close'])
            macd_result = self.calculate_macd(df['Close'])
            df['MACD'] = macd_result[0]
            df['Signal'] = macd_result[1]
            
            # Format data for frontend
            historical_data = []
            for index, row in df.iterrows():
                date_obj = row['Date']
                if hasattr(date_obj, 'strftime'):
                    date_str = date_obj.strftime('%Y-%m-%d')
                else:
                    date_str = str(date_obj)[:10]
                
                historical_data.append({
                    'date': date_str,
                    'open': safe_round(row.get('Open'), 2),
                    'high': safe_round(row.get('High'), 2),
                    'low': safe_round(row.get('Low'), 2),
                    'close': safe_round(row.get('Close'), 2),
                    'volume': safe_int(row.get('Volume'), 0),
                    'ma7': safe_round(row.get('MA7'), 2),
                    'ma20': safe_round(row.get('MA20'), 2),
                    'ma50': safe_round(row.get('MA50'), 2),
                    'rsi': safe_round(row.get('RSI'), 2),
                    'macd': safe_round(row.get('MACD'), 2),
                    'signal': safe_round(row.get('Signal'), 2)
                })
            
            return historical_data
        except Exception as e:
            print(f"Error fetching historical data for {self.ticker}: {str(e)}")
            return []
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Avoid division by zero
            loss_safe = loss.replace(0, np.nan)
            rs = gain / loss_safe
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            print(f"Error calculating RSI: {str(e)}")
            return pd.Series([np.nan] * len(prices))
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        try:
            exp1 = prices.ewm(span=fast, adjust=False).mean()
            exp2 = prices.ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal, adjust=False).mean()
            return macd, signal_line
        except Exception as e:
            print(f"Error calculating MACD: {str(e)}")
            empty_series = pd.Series([np.nan] * len(prices))
            return empty_series, empty_series
    
    def predict_prices(self, days=7):
        """Predict future stock prices using Linear Regression"""
        try:
            # Get 6 months of historical data
            df = self.stock.history(period='6mo')
            
            if len(df) < 30:
                print(f"Insufficient data for predictions: {len(df)} days")
                return None
            
            # Prepare data
            df = df.reset_index()
            df['Days'] = np.arange(len(df))
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df = df.dropna()
            
            if len(df) < 20:
                print("Insufficient data after cleaning")
                return None
            
            # Features and target
            X = df[['Days', 'Volume', 'MA5']].values
            y = df['Close'].values
            
            # Check for invalid values
            if np.any(np.isnan(X)) or np.any(np.isnan(y)):
                print("NaN values found in data")
                return None
            
            # Normalize features
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))
            
            # Train model
            model = LinearRegression()
            model.fit(X_scaled, y_scaled)
            
            # Make predictions
            last_day = len(df)
            last_volume = safe_float(df['Volume'].iloc[-1], df['Volume'].mean())
            last_ma5 = safe_float(df['MA5'].iloc[-1], df['Close'].iloc[-1])
            
            predictions = []
            current_ma5 = last_ma5
            
            for i in range(1, days + 1):
                future_day = last_day + i
                future_features = np.array([[future_day, last_volume, current_ma5]])
                future_features_scaled = scaler_X.transform(future_features)
                
                pred_scaled = model.predict(future_features_scaled)
                pred_price = safe_float(scaler_y.inverse_transform(pred_scaled)[0][0])
                
                # Update moving average for next prediction
                current_ma5 = (current_ma5 * 4 + pred_price) / 5
                
                pred_date = datetime.now() + timedelta(days=i)
                predictions.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'predictedPrice': safe_round(pred_price, 2)
                })
            
            # Calculate model confidence
            y_pred = model.predict(X_scaled)
            confidence = r2_score(y_scaled, y_pred)
            confidence_pct = max(0, min(100, confidence * 100))
            
            return {
                'predictions': predictions,
                'confidence': safe_round(confidence_pct, 2),
                'model': 'Linear Regression'
            }
            
        except Exception as e:
            print(f"Error making predictions for {self.ticker}: {str(e)}")
            return None
    
    def get_sentiment_signal(self):
        """Generate trading signal based on technical indicators"""
        try:
            df = self.stock.history(period='1mo')
            
            if len(df) < 20:
                return {
                    'signal': 'HOLD',
                    'strength': 0,
                    'rsi': None,
                    'price_vs_ma20': None
                }
            
            current_price = safe_float(df['Close'].iloc[-1])
            ma20 = safe_float(df['Close'].rolling(window=20).mean().iloc[-1])
            
            rsi_series = self.calculate_rsi(df['Close'])
            rsi_value = rsi_series.iloc[-1]
            rsi = safe_float(rsi_value, 50)
            
            signal_score = 0
            
            # Price vs MA20 signal
            if current_price > ma20:
                signal_score += 1
            else:
                signal_score -= 1
            
            # RSI signal
            if rsi < 30:
                signal_score += 2
            elif rsi > 70:
                signal_score -= 2
            
            # Determine final signal
            if signal_score >= 2:
                signal = 'STRONG BUY'
                strength = min(100, (signal_score / 3) * 100)
            elif signal_score == 1:
                signal = 'BUY'
                strength = 60
            elif signal_score == -1:
                signal = 'SELL'
                strength = 60
            elif signal_score <= -2:
                signal = 'STRONG SELL'
                strength = min(100, abs(signal_score / 3) * 100)
            else:
                signal = 'HOLD'
                strength = 50
            
            price_vs_ma20 = ((current_price - ma20) / ma20) * 100 if ma20 != 0 else 0
            
            return {
                'signal': signal,
                'strength': safe_round(strength, 2),
                'rsi': safe_round(rsi, 2),
                'price_vs_ma20': safe_round(price_vs_ma20, 2)
            }
            
        except Exception as e:
            print(f"Error calculating sentiment for {self.ticker}: {str(e)}")
            return {
                'signal': 'HOLD',
                'strength': 0,
                'rsi': None,
                'price_vs_ma20': None
            }


# API Routes
@app.route('/api/search/<query>', methods=['GET'])
def search_stocks(query: str):
    """Search for stocks by name or ticker"""
    try:
        suggestions = search_companies(query, limit=10)
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        print(f"Error in search_stocks: {str(e)}")
        return jsonify({'suggestions': []})


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    """Get complete stock analysis"""
    try:
        # Convert company name to ticker if needed
        actual_ticker = find_ticker(ticker)
        
        print(f"📊 Searching for: '{ticker}' → Resolved to: '{actual_ticker}'")
        
        analyzer = StockAnalyzer(actual_ticker)
        
        current_data = analyzer.get_current_data()
        if not current_data:
            return jsonify({
                'error': f'Invalid ticker or data unavailable for {ticker}',
                'searchedFor': ticker,
                'resolvedTo': actual_ticker
            }), 404
        
        historical_data = analyzer.get_historical_data(period='3mo')
        predictions = analyzer.predict_prices(days=7)
        sentiment = analyzer.get_sentiment_signal()
        
        return jsonify({
            'current': current_data,
            'historical': historical_data,
            'predictions': predictions,
            'sentiment': sentiment,
            'timestamp': datetime.now().isoformat(),
            'searchedFor': ticker,
            'actualTicker': actual_ticker
        })
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict/<ticker>/<int:days>', methods=['GET'])
def predict_stock(ticker: str, days: int):
    """Get price predictions"""
    try:
        if days > 30:
            return jsonify({'error': 'Maximum prediction period is 30 days'}), 400
        
        if days < 1:
            return jsonify({'error': 'Minimum prediction period is 1 day'}), 400
        
        # Convert company name to ticker if needed
        actual_ticker = find_ticker(ticker)
        analyzer = StockAnalyzer(actual_ticker)
        predictions = analyzer.predict_prices(days=days)
        
        if not predictions:
            return jsonify({'error': 'Unable to generate predictions'}), 500
        
        return jsonify(predictions)
        
    except Exception as e:
        print(f"Error in predict_stock: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Stock Analyzer API',
        'timestamp': datetime.now().isoformat(),
        'stocksAvailable': list(POPULAR_STOCKS.values())
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Stock Analyzer API',
        'version': '2.0.0',
        'features': [
            'Search by company name or ticker',
            'Real-time stock data',
            'ML price predictions',
            'Technical analysis (RSI, MACD, MA)',
            'Trading signals'
        ],
        'endpoints': {
            '/api/stock/<ticker>': 'Get full stock analysis (accepts name or ticker)',
            '/api/search/<query>': 'Search for stocks',
            '/api/predict/<ticker>/<days>': 'Get price predictions',
            '/health': 'Health check'
        },
        'stocksAvailable': len(set(POPULAR_STOCKS.values()))
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    
    print("=" * 50)
    print("🚀 Stock Analyzer API Starting...")
    print("=" * 50)
    print(f"📊 Mode: {'Development' if debug_mode else 'Production'}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"💡 Try: http://localhost:{port}/api/stock/AAPL")
    print(f"📈 Stocks available: {len(set(POPULAR_STOCKS.values()))}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)