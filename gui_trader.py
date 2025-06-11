import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from stock_trader import StockTrader
import threading
import time
from decimal import Decimal

class StockTraderGUI:
    def __init__(self):
        self.trader = StockTrader()
        
        # Configure the appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Stock Trading App")
        self.root.geometry("1200x800")
        
        # Create main containers
        self.create_header_frame()
        self.create_main_frame()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_prices, daemon=True)
        self.update_thread.start()

    def create_header_frame(self):
        """Create the header with balance and portfolio value"""
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)

        self.balance_label = ctk.CTkLabel(
            header_frame, 
            text=f"Balance: ${self.trader.balance:,.2f}",
            font=("Helvetica", 16)
        )
        self.balance_label.pack(side="left", padx=10)

        self.portfolio_value_label = ctk.CTkLabel(
            header_frame,
            text=f"Portfolio Value: ${self.trader.get_portfolio_value():,.2f}",
            font=("Helvetica", 16)
        )
        self.portfolio_value_label.pack(side="right", padx=10)

    def create_main_frame(self):
        """Create the main content area"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left side - Portfolio
        portfolio_frame = ctk.CTkFrame(main_frame)
        portfolio_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(portfolio_frame, text="Your Portfolio", font=("Helvetica", 20)).pack(pady=10)
        
        # Create Treeview for portfolio
        self.portfolio_tree = ttk.Treeview(
            portfolio_frame, 
            columns=("Symbol", "Shares", "Price", "Value", "Gain/Loss"),
            show="headings"
        )
        
        # Configure treeview columns
        for col in ("Symbol", "Shares", "Price", "Value", "Gain/Loss"):
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=100)
        
        self.portfolio_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Right side - Trading
        trading_frame = ctk.CTkFrame(main_frame)
        trading_frame.pack(side="right", fill="both", padx=5, pady=5)

        # Stock Search
        ctk.CTkLabel(trading_frame, text="Stock Trading", font=("Helvetica", 20)).pack(pady=10)
        
        search_frame = ctk.CTkFrame(trading_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        self.symbol_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter Stock Symbol")
        self.symbol_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame, 
            text="Search", 
            command=self.search_stock
        )
        search_button.pack(side="left", padx=5)

        # Stock Info Display
        self.stock_info_frame = ctk.CTkFrame(trading_frame)
        self.stock_info_frame.pack(fill="x", padx=5, pady=5)
        
        self.stock_name_label = ctk.CTkLabel(self.stock_info_frame, text="")
        self.stock_name_label.pack(pady=2)
        
        self.stock_price_label = ctk.CTkLabel(self.stock_info_frame, text="")
        self.stock_price_label.pack(pady=2)
        
        self.stock_change_label = ctk.CTkLabel(self.stock_info_frame, text="")
        self.stock_change_label.pack(pady=2)

        # Trading Controls
        trading_controls = ctk.CTkFrame(trading_frame)
        trading_controls.pack(fill="x", padx=5, pady=5)
        
        self.quantity_entry = ctk.CTkEntry(
            trading_controls, 
            placeholder_text="Quantity"
        )
        self.quantity_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(trading_controls)
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Buy",
            command=self.buy_stock,
            fg_color="green"
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="Sell",
            command=self.sell_stock,
            fg_color="red"
        ).pack(side="right", padx=5, expand=True)

    def search_stock(self):
        """Search for a stock and display its information"""
        symbol = self.symbol_entry.get().upper()
        info = self.trader.get_stock_info(symbol)
        
        if info:
            self.stock_name_label.configure(text=f"Name: {info['name']}")
            self.stock_price_label.configure(text=f"Price: ${info['price']:,.2f}")
            self.stock_change_label.configure(
                text=f"Change: {info['change']:.2f}%",
                text_color="green" if info['change'] > 0 else "red"
            )
        else:
            messagebox.showerror("Error", "Unable to fetch stock information")

    def buy_stock(self):
        """Handle buy stock action"""
        try:
            symbol = self.symbol_entry.get().upper()
            quantity = int(self.quantity_entry.get())
            success, message = self.trader.buy_stock(symbol, quantity)
            
            if success:
                messagebox.showinfo("Success", message)
                self.update_portfolio_display()
                self.update_balance_display()
            else:
                messagebox.showerror("Error", message)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")

    def sell_stock(self):
        """Handle sell stock action"""
        try:
            symbol = self.symbol_entry.get().upper()
            quantity = int(self.quantity_entry.get())
            success, message = self.trader.sell_stock(symbol, quantity)
            
            if success:
                messagebox.showinfo("Success", message)
                self.update_portfolio_display()
                self.update_balance_display()
            else:
                messagebox.showerror("Error", message)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")

    def update_portfolio_display(self):
        """Update the portfolio treeview"""
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
            
        for symbol, quantity in self.trader.portfolio.items():
            price = self.trader.get_stock_price(symbol)
            if price:
                value = price * quantity
                # In a real app, you would calculate the actual gain/loss
                # based on purchase price
                gain_loss = "N/A"  
                
                self.portfolio_tree.insert(
                    "", "end",
                    values=(symbol, quantity, f"${price:,.2f}", 
                           f"${value:,.2f}", gain_loss)
                )

    def update_balance_display(self):
        """Update the balance and portfolio value display"""
        self.balance_label.configure(
            text=f"Balance: ${self.trader.balance:,.2f}"
        )
        self.portfolio_value_label.configure(
            text=f"Portfolio Value: ${self.trader.get_portfolio_value():,.2f}"
        )

    def update_prices(self):
        """Update prices periodically"""
        while True:
            self.update_portfolio_display()
            self.update_balance_display()
            time.sleep(60)  # Update every minute

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = StockTraderGUI()
    app.run()
