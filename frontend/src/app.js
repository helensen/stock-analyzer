import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Area, AreaChart } from 'recharts';
import { TrendingUp, DollarSign, Search, AlertCircle, Activity, Target, Zap, Brain } from 'lucide-react';

const StockAnalyzer = () => {
  const [ticker, setTicker] = useState('');
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedModel, setSelectedModel] = useState('linear');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const fetchStockData = async () => {
    if (!ticker.trim()) {
      setError('Please enter a stock ticker or company name');
      return;
    }

    setLoading(true);
    setError('');
    setShowSuggestions(false);

    try {
      const response = await fetch(`${API_URL}/stock/${ticker}?model=${selectedModel}`);
      
      if (!response.ok) {
        throw new Error('Stock data not found');
      }

      const data = await response.json();
      setStockData(data);
    } catch (err) {
      setError(`Failed to fetch data: ${err.message}. Try a different ticker or company name.`);
      setStockData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async (query) => {
    if (query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/search/${query}`);
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setShowSuggestions(data.suggestions && data.suggestions.length > 0);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
      setSuggestions([]);
    }
  };

  const handleSearchInput = (value) => {
    setTicker(value);
    
    if (value.length >= 2) {
      setTimeout(() => {
        fetchSuggestions(value);
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setTicker(suggestion.ticker);
    setSuggestions([]);
    setShowSuggestions(false);
    
    setTimeout(() => {
      const tempTicker = suggestion.ticker;
      setTicker(tempTicker);
      fetchStockDataWithTicker(tempTicker);
    }, 100);
  };

  const fetchStockDataWithTicker = async (tickerValue) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/stock/${tickerValue}?model=${selectedModel}`);
      
      if (!response.ok) {
        throw new Error('Stock data not found');
      }

      const data = await response.json();
      setStockData(data);
    } catch (err) {
      setError(`Failed to fetch data: ${err.message}`);
      setStockData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchStockData();
    }
  };

  const handleQuickSearch = (tickerValue) => {
    setTicker(tickerValue);
    setShowSuggestions(false);
    setTimeout(() => fetchStockDataWithTicker(tickerValue), 100);
  };

  const getSignalColor = (signal) => {
    if (signal?.includes('BUY')) return 'text-green-400';
    if (signal?.includes('SELL')) return 'text-red-400';
    return 'text-yellow-400';
  };

  const getSignalBgColor = (signal) => {
    if (signal?.includes('BUY')) return 'bg-green-500/20 border-green-500';
    if (signal?.includes('SELL')) return 'bg-red-500/20 border-red-500';
    return 'bg-yellow-500/20 border-yellow-500';
  };

  const getCombinedChartData = () => {
    if (!stockData) return [];
    
    const historical = stockData.historical.map(item => ({
      date: item.date,
      actual: item.close,
      ma7: item.ma7,
      ma20: item.ma20,
      predicted: null
    }));

    const predictions = stockData.predictions?.predictions?.map(item => ({
      date: item.date,
      actual: null,
      ma7: null,
      ma20: null,
      predicted: item.predictedPrice
    })) || [];

    return [...historical, ...predictions];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center justify-center gap-3">
            <TrendingUp className="text-green-400" size={36} />
            AI Stock Analyzer
          </h1>
          <p className="text-slate-400">Real-time data + Machine Learning predictions</p>
        </div>

        {/* Search Bar */}
        <div className="bg-slate-800 rounded-xl shadow-2xl p-6 mb-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[300px] relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Enter stock ticker or company name (e.g., AAPL or Apple)"
                value={ticker}
                onChange={(e) => handleSearchInput(e.target.value)}
                onKeyPress={handleKeyPress}
                onFocus={() => {
                  if (suggestions.length > 0) setShowSuggestions(true);
                }}
                onBlur={() => {
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
                className="w-full pl-12 pr-4 py-3 bg-slate-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              
              {/* Suggestions Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-slate-700 rounded-lg shadow-xl border border-slate-600 max-h-64 overflow-y-auto">
                  {suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="px-4 py-3 hover:bg-slate-600 cursor-pointer border-b border-slate-600 last:border-b-0 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-blue-400 font-semibold">{suggestion.ticker}</span>
                          <span className="text-slate-300 ml-2">- {suggestion.name}</span>
                        </div>
                        <Search className="text-slate-500" size={16} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Model Selector */}
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="px-4 py-3 bg-slate-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              title="Choose prediction model"
            >
              <option value="linear">⚡ Fast (~1s)</option>
              <option value="lstm">🤖 Accurate (~30s)</option>
            </select>
            
            <button
              onClick={fetchStockData}
              disabled={loading}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  {selectedModel === 'lstm' ? 'Training AI...' : 'Analyzing...'}
                </>
              ) : (
                'Analyze'
              )}
            </button>
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500 rounded-lg flex items-start gap-2">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-red-400">{error}</p>
            </div>
          )}
          
          {/* Model Info */}
          <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
            <div className="flex items-start gap-2 text-sm">
              {selectedModel === 'linear' ? (
                <>
                  <Zap className="text-yellow-400 flex-shrink-0 mt-0.5" size={16} />
                  <div>
                    <p className="text-slate-300"><strong>Fast Mode:</strong> Uses Linear Regression for quick predictions (~1 second)</p>
                  </div>
                </>
              ) : (
                <>
                  <Brain className="text-purple-400 flex-shrink-0 mt-0.5" size={16} />
                  <div>
                    <p className="text-slate-300"><strong>Accurate Mode:</strong> Uses LSTM Neural Network for better predictions (~30 seconds)</p>
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* Popular Searches */}
          <div className="mt-4">
            <p className="text-slate-400 text-sm mb-2">💡 Popular searches:</p>
            <div className="flex flex-wrap gap-2">
              {['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'NFLX'].map(t => (
                <button
                  key={t}
                  onClick={() => handleQuickSearch(t)}
                  className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-sm transition-colors"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stock Data Display */}
        {stockData && (
          <div className="space-y-6">
            {/* Company Name */}
            <div className="bg-slate-800 rounded-xl p-4 shadow-lg">
              <h2 className="text-2xl font-bold text-white">{stockData.current.companyName}</h2>
              <div className="flex items-center gap-4 mt-1">
                <p className="text-slate-400">{stockData.current.symbol}</p>
                {stockData.predictions && (
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded border border-blue-500">
                    {stockData.predictions.model}
                  </span>
                )}
              </div>
              {stockData.searchedFor && stockData.searchedFor !== stockData.actualTicker && (
                <p className="text-sm text-blue-400 mt-1">
                  Searched for: "{stockData.searchedFor}" → Found: {stockData.actualTicker}
                </p>
              )}
            </div>

            {/* Stock Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Current Price</span>
                  <DollarSign className="text-green-400" size={20} />
                </div>
                <p className="text-3xl font-bold text-white">${stockData.current.currentPrice}</p>
                <p className={`text-sm mt-1 ${stockData.current.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {stockData.current.change >= 0 ? '+' : ''}{stockData.current.change} ({stockData.current.changePercent}%)
                </p>
              </div>

              <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">52W High / Low</span>
                  <Activity className="text-blue-400" size={20} />
                </div>
                <p className="text-2xl font-bold text-white">${stockData.current.high52Week}</p>
                <p className="text-sm text-red-400 mt-1">${stockData.current.low52Week}</p>
              </div>

              <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Volume</span>
                  <Activity className="text-purple-400" size={20} />
                </div>
                <p className="text-2xl font-bold text-white">{(stockData.current.volume / 1000000).toFixed(2)}M</p>
                <p className="text-sm text-slate-400 mt-1">shares traded</p>
              </div>

              <div className={`rounded-xl p-6 shadow-lg border-2 ${getSignalBgColor(stockData.sentiment?.signal)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">AI Signal</span>
                  <Target className={getSignalColor(stockData.sentiment?.signal)} size={20} />
                </div>
                <p className={`text-2xl font-bold ${getSignalColor(stockData.sentiment?.signal)}`}>
                  {stockData.sentiment?.signal || 'HOLD'}
                </p>
                <p className="text-sm text-slate-400 mt-1">
                  Confidence: {stockData.sentiment?.strength || 0}%
                </p>
              </div>
            </div>

            {/* Technical Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                <h3 className="text-lg font-bold text-white mb-4">Technical Indicators</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">RSI (14)</span>
                    <span className={`font-semibold ${
                      stockData.sentiment?.rsi < 30 ? 'text-green-400' :
                      stockData.sentiment?.rsi > 70 ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {stockData.sentiment?.rsi?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Price vs MA20</span>
                    <span className={`font-semibold ${
                      stockData.sentiment?.price_vs_ma20 > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {stockData.sentiment?.price_vs_ma20?.toFixed(2) || 'N/A'}%
                    </span>
                  </div>
                </div>
              </div>

              {stockData.predictions && (
                <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                  <h3 className="text-lg font-bold text-white mb-4">7-Day Prediction</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Predicted Price (7d)</span>
                      <span className="font-semibold text-blue-400">
                        ${stockData.predictions.predictions[stockData.predictions.predictions.length - 1]?.predictedPrice}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Model Confidence</span>
                      <span className="font-semibold text-green-400">
                        {stockData.predictions.confidence}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Model Type</span>
                      <span className="font-semibold text-slate-300">
                        {stockData.predictions.model}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Rest of the charts remain the same... */}
            {/* Price Chart with Predictions */}
            <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-bold text-white mb-4">Price History & AI Predictions</h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={getCombinedChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                    labelStyle={{ color: '#cbd5e1' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2} name="Actual Price" dot={false} />
                  <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" name="AI Prediction" dot={false} />
                  <Line type="monotone" dataKey="ma7" stroke="#10b981" strokeWidth={1.5} name="7-Day MA" dot={false} opacity={0.6} />
                  <Line type="monotone" dataKey="ma20" stroke="#8b5cf6" strokeWidth={1.5} name="20-Day MA" dot={false} opacity={0.6} />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-slate-400 text-sm mt-2 text-center">
                Dashed orange line shows ML-predicted prices for the next 7 days
              </p>
            </div>

            {/* RSI Chart */}
            {stockData.historical.some(d => d.rsi) && (
              <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
                <h2 className="text-xl font-bold text-white mb-4">RSI Indicator</h2>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={stockData.historical}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <XAxis dataKey="date" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                      labelStyle={{ color: '#cbd5e1' }}
                    />
                    <Area type="monotone" dataKey="rsi" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
                <div className="flex justify-between text-sm mt-2">
                  <span className="text-green-400">Oversold &lt; 30</span>
                  <span className="text-yellow-400">Neutral 30-70</span>
                  <span className="text-red-400">Overbought &gt; 70</span>
                </div>
              </div>
            )}

            {/* Volume Chart */}
            <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-bold text-white mb-4">Trading Volume</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stockData.historical}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                    labelStyle={{ color: '#cbd5e1' }}
                  />
                  <Bar dataKey="volume" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Price Details Table */}
            <div className="bg-slate-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-bold text-white mb-4">Recent Price Action</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-slate-400 font-semibold">Date</th>
                      <th className="text-right py-3 px-4 text-slate-400 font-semibold">Open</th>
                      <th className="text-right py-3 px-4 text-slate-400 font-semibold">High</th>
                      <th className="text-right py-3 px-4 text-slate-400 font-semibold">Low</th>
                      <th className="text-right py-3 px-4 text-slate-400 font-semibold">Close</th>
                      <th className="text-right py-3 px-4 text-slate-400 font-semibold">RSI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stockData.historical.slice(-10).reverse().map((day, index) => (
                      <tr key={index} className="border-b border-slate-700 hover:bg-slate-700 transition-colors">
                        <td className="py-3 px-4 text-white">{day.date}</td>
                        <td className="py-3 px-4 text-right text-slate-300">${day.open}</td>
                        <td className="py-3 px-4 text-right text-green-400">${day.high}</td>
                        <td className="py-3 px-4 text-right text-red-400">${day.low}</td>
                        <td className="py-3 px-4 text-right text-white font-semibold">${day.close}</td>
                        <td className={`py-3 px-4 text-right font-semibold ${
                          day.rsi < 30 ? 'text-green-400' :
                          day.rsi > 70 ? 'text-red-400' : 'text-yellow-400'
                        }`}>
                          {day.rsi ? day.rsi.toFixed(2) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Welcome Message */}
        {!stockData && !loading && (
          <div className="bg-slate-800 rounded-xl p-12 text-center shadow-lg">
            <TrendingUp className="mx-auto text-slate-600 mb-4" size={64} />
            <h3 className="text-2xl font-bold text-white mb-2">Start Analyzing Stocks with AI</h3>
            <p className="text-slate-400 mb-4">Enter a stock ticker OR company name to view real-time data, technical indicators, and ML price predictions</p>
            <div className="bg-slate-700 rounded-lg p-4 mt-4 max-w-md mx-auto">
              <p className="text-sm text-slate-300 mb-2">✨ Try searching for:</p>
              <div className="text-left space-y-1 text-sm text-slate-400">
                <p>• Ticker: <span className="text-blue-400">AAPL</span> or Company: <span className="text-blue-400">Apple</span></p>
                <p>• Ticker: <span className="text-blue-400">TSLA</span> or Company: <span className="text-blue-400">Tesla</span></p>
                <p>• Ticker: <span className="text-blue-400">MSFT</span> or Company: <span className="text-blue-400">Microsoft</span></p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockAnalyzer;