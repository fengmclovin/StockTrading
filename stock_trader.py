import yfinance as yf
import pandas as pd
from datetime import datetime
from decimal import Decimal
import json
import os

class StockTrader:
    def __init__(self):
        self.portfolio = {}
        self.balance = Decimal('100000')  # Starting with $100,000
        self.load_portfolio()

    def load_portfolio(self):
        """Load portfolio from file if exists"""
        try:
            with open('portfolio.json', 'r') as f:
                data = json.load(f)
                self.portfolio = {k: Decimal(str(v)) for k, v in data['portfolio'].items()}
                self.balance = Decimal(str(data['balance']))
        except FileNotFoundError:
            pass

    def save_portfolio(self):
        """Save portfolio to file"""
        with open('portfolio.json', 'w') as f:
            data = {
                'portfolio': {k: str(v) for k, v in self.portfolio.items()},
                'balance': str(self.balance)
            }
            json.dump(data, f)

    def get_stock_price(self, symbol):
        """Get current stock price"""
        try:
            stock = yf.Ticker(symbol)
            return Decimal(str(stock.info['regularMarketPrice']))
        except:
            return None

    def get_stock_info(self, symbol):
        """Get detailed stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'price': info.get('regularMarketPrice', 'N/A'),
                'change': info.get('regularMarketChangePercent', 'N/A'),
                'volume': info.get('volume', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('forwardPE', 'N/A')
            }
        except:
            return None

    def buy_stock(self, symbol, quantity):
        """Buy stocks"""
        price = self.get_stock_price(symbol)
        if not price:
            return False, "Unable to get stock price"

        total_cost = price * Decimal(str(quantity))
        if total_cost > self.balance:
            return False, "Insufficient funds"

        self.balance -= total_cost
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        self.save_portfolio()
        return True, f"Successfully bought {quantity} shares of {symbol}"

    def sell_stock(self, symbol, quantity):
        """Sell stocks"""
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False, "Insufficient shares"

        price = self.get_stock_price(symbol)
        if not price:
            return False, "Unable to get stock price"

        total_value = price * Decimal(str(quantity))
        self.balance += total_value
        self.portfolio[symbol] -= quantity
        
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        self.save_portfolio()
        return True, f"Successfully sold {quantity} shares of {symbol}"

    def get_portfolio_value(self):
        """Calculate total portfolio value"""
        total_value = self.balance
        for symbol, quantity in self.portfolio.items():
            price = self.get_stock_price(symbol)
            if price:
                total_value += price * quantity
        return total_value
