import tkinter as tk
from tkinter import messagebox, ttk
import math
import json
import os
from ast import literal_eval

class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize settings
        self.history_file = "calculator_history.json"
        self.theme_dark = True
        self.load_history()
        
        # Setting up the main window
        self.title("Advanced Calculator")
        self.geometry("450x600")  # Slightly taller for new features
        self.resizable(False, False)
        self.apply_theme()  # Apply initial theme
        
        # This tracks which mode we're in
        self.mode = tk.StringVar(value="Standard")
        self.create_top_bar()
        self.create_mode_selector()
        
        # The display where numbers and results show up
        self.display = tk.Entry(
            self, 
            font=("Arial", 22), 
            bd=0,
            justify="right"
        )
        self.display.pack(fill=tk.X, padx=10, pady=(10, 0), ipady=10)
        
        # Add keyboard bindings
        self.bind_keyboard_events()
        
        # This frame will hold all our calculator buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(padx=10, pady=10)
        
        # Create the initial set of buttons
        self.create_buttons()
        self.history = []  # Will be loaded from file

    def create_top_bar(self):
        """Creates the top bar with theme toggle and export buttons"""
        top_frame = tk.Frame(self, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # Theme toggle
        self.theme_btn = tk.Button(
            top_frame,
            text="🌙 Dark",
            font=("Arial", 10),
            command=self.toggle_theme,
            bg=self.colors['button_special'],
            fg=self.colors['text'],
            bd=0,
            width=8
        )
        self.theme_btn.pack(side=tk.LEFT)
        
        # Export button
        export_btn = tk.Button(
            top_frame,
            text="💾 Export",
            font=("Arial", 10),
            command=self.export_history,
            bg=self.colors['button_special'],
            fg=self.colors['text'],
            bd=0,
            width=8
        )
        export_btn.pack(side=tk.LEFT, padx=(5, 0))

    def create_mode_selector(self):
        """Creates mode switcher buttons with new modes"""
        mode_frame = tk.Frame(self, bg=self.colors['bg'])
        mode_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # Added Currency and Unit converter modes
        modes = ["Standard", "Scientific", "Programmer", "Currency", "Unit"]
        for m in modes:
            rb = tk.Radiobutton(
                mode_frame, 
                text=m, 
                variable=self.mode, 
                value=m,
                font="Arial 10", 
                bg=self.colors['mode_bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['mode_selected'],
                activebackground=self.colors['mode_hover'],
                indicatoron=0,
                width=10, 
                bd=0,
                relief=tk.FLAT, 
                command=self.update_mode
            )
            rb.pack(side=tk.LEFT, padx=2)

    def apply_theme(self):
        """Applies current theme colors"""
        if self.theme_dark:
            self.colors = {
                'bg': "#22223b",
                'display_bg': "#f2e9e4", 
                'display_fg': "#22223b",
                'text': "#f2e9e4",
                'button_regular': "#9a8c98",
                'button_special': "#4a4e69",
                'button_equals': "#c9ada7",
                'mode_bg': "#4a4e69",
                'mode_selected': "#c9ada7",
                'mode_hover': "#9a8c98"
            }
        else:
            self.colors = {
                'bg': "#f0f0f0",
                'display_bg': "#ffffff", 
                'display_fg': "#000000",
                'text': "#000000",
                'button_regular': "#e0e0e0",
                'button_special': "#a0a0a0", 
                'button_equals': "#87CEEB",
                'mode_bg': "#d0d0d0",
                'mode_selected': "#87CEEB",
                'mode_hover': "#c0c0c0"
            }
        
        # Apply colors to window and widgets
        self.configure(bg=self.colors['bg'])
        if hasattr(self, 'display'):
            self.display.configure(bg=self.colors['display_bg'], fg=self.colors['display_fg'])

    def toggle_theme(self):
        """Switches between dark and light themes"""
        self.theme_dark = not self.theme_dark
        self.theme_btn.config(text="☀️ Light" if not self.theme_dark else "🌙 Dark")
        self.apply_theme()
        self.create_buttons()  # Recreate buttons with new colors

    def bind_keyboard_events(self):
        """Bind keyboard keys to calculator functions"""
        # Number keys
        for key in "0123456789":
            self.bind(f"<Key-{key}>", lambda e, k=key: self.on_button_click(k))
        
        # Operator keys
        self.bind("<Key-plus>", lambda e: self.on_button_click('+'))
        self.bind("<Key-minus>", lambda e: self.on_button_click('-'))
        self.bind("<Key-asterisk>", lambda e: self.on_button_click('*'))
        self.bind("<Key-slash>", lambda e: self.on_button_click('/'))
        self.bind("<Key-period>", lambda e: self.on_button_click('.'))
        self.bind("<Key-Return>", lambda e: self.calculate())
        self.bind("<Key-Escape>", lambda e: self.on_button_click('C'))
        self.bind("<Key-BackSpace>", self.handle_backspace)
        
        # Focus the display so keys work immediately
        self.display.focus_set()

    def handle_backspace(self, event):
        """Handle backspace key press"""
        current = self.display.get()
        if current:
            self.display.delete(0, tk.END)
            self.display.insert(0, current[:-1])

    def create_buttons(self):
        """Builds the calculator buttons - different layouts for each mode"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()
            
        mode = self.mode.get()
        
        if mode == "Standard":
            buttons = [
                ['7', '8', '9', '/', 'C'],
                ['4', '5', '6', '*', '('],
                ['1', '2', '3', '-', ')'],
                ['0', '.', '=', '+', 'His']
            ]
        elif mode == "Scientific":
            buttons = [
                ['sin', 'cos', 'tan', 'log', 'C'],
                ['sqrt', 'exp', '^', 'pi', '('],
                ['7', '8', '9', '/', ')'],
                ['4', '5', '6', '*', 'His'],
                ['1', '2', '3', '-', ''],
                ['0', '.', '=', '+', '']
            ]
        elif mode == "Programmer":
            buttons = [
                ['A', 'B', 'C', 'D', 'E'],
                ['F', '(', ')', '<<', '>>'],
                ['7', '8', '9', '&', '|'],
                ['4', '5', '6', '^', '~'],
                ['1', '2', '3', '+', '-'],
                ['0', '.', '=', 'C', 'His']
            ]
        elif mode == "Currency":
            buttons = [
                ['USD', 'EUR', 'GBP', 'JPY', 'C'],
                ['7', '8', '9', '/', 'CAD'],
                ['4', '5', '6', '*', 'AUD'],
                ['1', '2', '3', '-', 'CHF'],
                ['0', '.', '=', '+', 'His']
            ]
        elif mode == "Unit":
            buttons = [
                ['cm→m', 'm→ft', 'kg→lb', '°C→°F', 'C'],
                ['7', '8', '9', '/', 'km→mi'],
                ['4', '5', '6', '*', 'L→gal'],
                ['1', '2', '3', '-', 'm²→ft²'],
                ['0', '.', '=', '+', 'His']
            ]
            
        # Tooltip dictionary
        tooltips = {
            'sin': 'Sine function', 'cos': 'Cosine function', 'tan': 'Tangent function',
            'log': 'Logarithm base 10', 'sqrt': 'Square root', 'exp': 'Exponential',
            'pi': 'Pi (3.14159...)', '<<': 'Bitwise left shift', '>>': 'Bitwise right shift',
            '&': 'Bitwise AND', '|': 'Bitwise OR', '~': 'Bitwise NOT', '^': 'Bitwise XOR',
            'USD': 'US Dollar', 'EUR': 'Euro', 'GBP': 'British Pound', 'JPY': 'Japanese Yen',
            'CAD': 'Canadian Dollar', 'AUD': 'Australian Dollar', 'CHF': 'Swiss Franc',
            'cm→m': 'Centimeters to Meters', 'm→ft': 'Meters to Feet', 'kg→lb': 'Kilograms to Pounds',
            '°C→°F': 'Celsius to Fahrenheit', 'km→mi': 'Kilometers to Miles', 'L→gal': 'Liters to Gallons',
            'm²→ft²': 'Square meters to Square feet'
        }
        
        for r, row in enumerate(buttons):
            for c, btn in enumerate(row):
                if btn == '':
                    continue
                    
                # Color coding
                if btn in ('=', 'C', 'His'):
                    if btn == '=':
                        bg_color = self.colors['button_equals']
                    else:
                        bg_color = self.colors['button_special']
                else:
                    bg_color = self.colors['button_regular']
                
                b = tk.Button(
                    self.button_frame, 
                    text=btn, 
                    font=("Arial", 12, "bold"),
                    bg=bg_color,
                    fg=self.colors['display_fg'],
                    width=6, 
                    height=2, 
                    bd=0,
                    relief=tk.RAISED,
                    command=lambda val=btn: self.on_button_click(val)
                )
                b.grid(row=r, column=c, padx=2, pady=2)
                
                # Add tooltip
                if btn in tooltips:
                    self.create_tooltip(b, tooltips[btn])

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.bind("<Leave>", lambda e: hide_tooltip())
        
        widget.bind("<Enter>", show_tooltip)

    def update_mode(self):
        """Switches between calculator modes"""
        self.display.delete(0, tk.END)
        self.create_buttons()

    def on_button_click(self, value):
        """Handles button clicks"""
        if value == 'C':
            self.display.delete(0, tk.END)
        elif value == '=':
            self.calculate()
        elif value == 'His':
            self.show_history()
        else:
            # Handle special modes
            if self.mode.get() in ["Currency", "Unit"]:
                self.handle_conversion(value)
            else:
                display_value = value if value != '^' else '**'
                self.display.insert(tk.END, display_value)

    def handle_conversion(self, conversion_type):
        """Handle currency and unit conversions"""
        try:
            amount = float(self.display.get())
            result = self.perform_conversion(amount, conversion_type)
            self.display.delete(0, tk.END)
            self.display.insert(0, str(round(result, 4)))
            self.history.append(f"{amount} {conversion_type} = {result}")
            self.save_history()
        except:
            messagebox.showerror("Error", "Enter a valid number first")

    def perform_conversion(self, amount, conversion_type):
        """Perform the actual conversion calculations"""
        # Simple conversion rates (you'd want real API for currency)
        conversions = {
            # Currency rates (example rates)
            'USD→EUR': 0.85, 'EUR→USD': 1.18, 'USD→GBP': 0.73, 'GBP→USD': 1.37,
            'USD→JPY': 110.0, 'JPY→USD': 0.0091, 'USD→CAD': 1.25, 'CAD→USD': 0.80,
            'USD→AUD': 1.35, 'AUD→USD': 0.74, 'USD→CHF': 0.92, 'CHF→USD': 1.09,
            
            # Unit conversions
            'cm→m': 0.01, 'm→cm': 100, 'm→ft': 3.28084, 'ft→m': 0.3048,
            'kg→lb': 2.20462, 'lb→kg': 0.453592, '°C→°F': lambda x: (x * 9/5) + 32,
            '°F→°C': lambda x: (x - 32) * 5/9, 'km→mi': 0.621371, 'mi→km': 1.60934,
            'L→gal': 0.264172, 'gal→L': 3.78541, 'm²→ft²': 10.7639, 'ft²→m²': 0.092903
        }
        
        if conversion_type in conversions:
            conversion = conversions[conversion_type]
            if callable(conversion):
                return conversion(amount)
            return amount * conversion
        return amount

    def calculate(self):
        """Evaluates the math expression safely"""
        expr = self.display.get()
        mode = self.mode.get()
        
        if not expr:
            return
            
        try:
            if mode == "Scientific":
                expr = self.process_scientific_expression(expr)
            elif mode == "Programmer":
                expr = self.process_programmer_expression(expr)
            
            # Safer evaluation using literal_eval for basic expressions
            if all(c in '0123456789+-*/.() ' for c in expr.replace(' ', '')):
                result = literal_eval(expr)
            else:
                # For complex expressions, use eval but restricted
                result = eval(expr, {"math": math, "__builtins__": {}}, {})
            
            self.display.delete(0, tk.END)
            self.display.insert(0, str(result))
            self.history.append(f"{expr} = {result}")
            self.save_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid Expression: {str(e)}")

    def process_scientific_expression(self, expr):
        """Process scientific expressions safely"""
        replacements = {
            'pi': str(math.pi),
            'sin': 'math.sin', 'cos': 'math.cos', 'tan': 'math.tan',
            'log': 'math.log10', 'sqrt': 'math.sqrt', 'exp': 'math.exp'
        }
        
        for find, replace in replacements.items():
            expr = expr.replace(find, replace)
        return expr

    def process_programmer_expression(self, expr):
        """Process programmer expressions"""
        # Bitwise operations
        expr = expr.replace('<<', '<<').replace('>>', '>>')
        expr = expr.replace('&', '&').replace('|', '|').replace('~', '~')
        
        # Hex to decimal conversion
        for ch in 'ABCDEF':
            expr = expr.replace(ch, str(int(ch, 16)))
        return expr

    def load_history(self):
        """Load history from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except:
            self.history = []

    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-100:], f)  # Keep last 100 entries
        except:
            pass  # Silently fail if can't save

    def export_history(self):
        """Export history to text file"""
        try:
            with open("calculator_export.txt", "w") as f:
                f.write("Calculator History Export\n")
                f.write("=" * 30 + "\n")
                for item in self.history:
                    f.write(item + "\n")
            messagebox.showinfo("Success", "History exported to calculator_export.txt")
        except:
            messagebox.showerror("Error", "Could not export history")

    def show_history(self):
        """Show calculation history"""
        history_win = tk.Toplevel(self)
        history_win.title("Calculation History")
        history_win.geometry("400x350")
        history_win.configure(bg=self.colors['bg'])
        
        # Add clear button
        clear_btn = tk.Button(
            history_win, 
            text="Clear History",
            command=lambda: self.clear_history(history_win),
            bg=self.colors['button_special'],
            fg=self.colors['text']
        )
        clear_btn.pack(pady=5)
        
        text = tk.Text(history_win, font=("Arial", 11), bg=self.colors['display_bg'], fg=self.colors['display_fg'])
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for item in self.history[-50:]:  # Show last 50 entries
            text.insert(tk.END, item + "\n")
            
        text.config(state=tk.DISABLED)

    def clear_history(self, window):
        """Clear the history"""
        self.history = []
        self.save_history()
        window.destroy()
        messagebox.showinfo("Success", "History cleared")

    def on_closing(self):
        """Save history when closing"""
        self.save_history()
        self.destroy()

if __name__ == "__main__":
    app = AdvancedCalculator()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()