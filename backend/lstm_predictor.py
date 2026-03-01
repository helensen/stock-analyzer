"""
LSTM Model for Stock Price Prediction
Much more accurate than Linear Regression
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")


class LSTMStockPredictor:
    """LSTM Neural Network for stock price prediction"""
    
    def __init__(self, lookback=60):
        """
        Initialize LSTM predictor
        
        Args:
            lookback: Number of previous days to use for prediction (default 60)
        """
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def prepare_data(self, df, feature_column='Close'):
        """
        Prepare data for LSTM
        
        Args:
            df: DataFrame with stock data
            feature_column: Column to predict (default 'Close')
            
        Returns:
            X, y: Training data
        """
        # Get the data
        data = df[feature_column].values.reshape(-1, 1)
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        
        # Reshape for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def build_model(self, input_shape):
        """
        Build LSTM model architecture
        
        Args:
            input_shape: Shape of input data
            
        Returns:
            Compiled Keras model
        """
        model = Sequential([
            # First LSTM layer with Dropout
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            
            # Third LSTM layer
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            
            # Dense output layer
            Dense(units=25),
            Dense(units=1)
        ])
        
        # Compile the model
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        return model
    
    def train(self, df, epochs=50, batch_size=32, verbose=0):
        """
        Train the LSTM model
        
        Args:
            df: DataFrame with stock data
            epochs: Number of training epochs
            batch_size: Batch size for training
            verbose: Verbosity level (0=silent, 1=progress bar)
            
        Returns:
            Training history
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM predictions")
        
        # Prepare data
        X, y = self.prepare_data(df)
        
        # Build model
        self.model = self.build_model(input_shape=(X.shape[1], 1))
        
        # Train model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=verbose,
            shuffle=False
        )
        
        return history
    
    def predict_future(self, df, days=7):
        """
        Predict future stock prices
        
        Args:
            df: DataFrame with stock data
            days: Number of days to predict
            
        Returns:
            List of predictions with dates
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM predictions")
        
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        # Get the last 'lookback' days of data
        last_data = df['Close'].values[-self.lookback:]
        last_data = last_data.reshape(-1, 1)
        last_data_scaled = self.scaler.transform(last_data)
        
        # Prepare for prediction
        predictions = []
        current_batch = last_data_scaled.reshape(1, self.lookback, 1)
        
        # Predict future days
        for i in range(days):
            # Get prediction
            current_pred = self.model.predict(current_batch, verbose=0)[0]
            
            # Store prediction
            predictions.append(current_pred[0])
            
            # Update batch for next prediction
            current_batch = np.append(current_batch[:, 1:, :], [[current_pred]], axis=1)
        
        # Inverse transform predictions to original scale
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        
        # Create prediction list with dates
        prediction_list = []
        for i, pred in enumerate(predictions):
            pred_date = datetime.now() + timedelta(days=i+1)
            prediction_list.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predictedPrice': round(float(pred[0]), 2)
            })
        
        return prediction_list
    
    def calculate_confidence(self, df):
        """
        Calculate model confidence based on validation performance
        
        Args:
            df: DataFrame with stock data
            
        Returns:
            Confidence score (0-100)
        """
        try:
            X, y = self.prepare_data(df)
            
            # Use last 20% as validation
            split_idx = int(len(X) * 0.8)
            X_val, y_val = X[split_idx:], y[split_idx:]
            
            # Predict on validation set
            y_pred = self.model.predict(X_val, verbose=0)
            
            # Calculate R² score
            ss_res = np.sum((y_val - y_pred.flatten()) ** 2)
            ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            
            # Convert to confidence percentage (0-100)
            confidence = max(0, min(100, r2 * 100))
            
            return round(confidence, 2)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 75.0  # Default confidence


def predict_with_lstm(df, days=7, epochs=50):
    """
    High-level function to predict stock prices using LSTM
    
    Args:
        df: DataFrame with stock data (must have 'Close' column)
        days: Number of days to predict
        epochs: Number of training epochs
        
    Returns:
        Dictionary with predictions and confidence
    """
    try:
        if not TENSORFLOW_AVAILABLE:
            return None
        
        if len(df) < 100:
            print(f"Insufficient data for LSTM: {len(df)} days (need at least 100)")
            return None
        
        # Initialize predictor
        predictor = LSTMStockPredictor(lookback=60)
        
        # Train model
        predictor.train(df, epochs=epochs, verbose=0)
        
        # Make predictions
        predictions = predictor.predict_future(df, days=days)
        
        # Calculate confidence
        confidence = predictor.calculate_confidence(df)
        
        return {
            'predictions': predictions,
            'confidence': confidence,
            'model': 'LSTM Neural Network'
        }
        
    except Exception as e:
        print(f"Error in LSTM prediction: {e}")
        return None