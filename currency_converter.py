import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

HISTORY_FILE = "conversion_history.json"

# Список популярных валют
CURRENCIES = [
    "USD", "EUR", "RUB", "GBP", "JPY", "CNY", "CAD", "CHF", 
    "AUD", "INR", "TRY", "BRL", "KRW", "SGD", "NOK", "SEK", 
    "PLN", "UAH", "KZT", "AED", "HKD", "MXN", "ZAR", "NZD"
]

# Бесплатный API без ключа (Open Exchange Rate API)
API_URL = "https://api.exchangerate-api.com/v4/latest/"


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter - Конвертер валют")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.history = []
        self.load_history()

        self.create_widgets()
        self.refresh_history_table()

    def create_widgets(self):
        # === Рамка конвертации ===
        convert_frame = tk.LabelFrame(self.root, text="Конвертация валют", padx=15, pady=15)
        convert_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(convert_frame, text="Сумма:").grid(row=0, column=0, sticky="e", padx=5, pady=10)
        self.amount_entry = tk.Entry(convert_frame, width=15, font=("Arial", 12))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=10)
        self.amount_entry.insert(0, "100")

        # Из валюты
        tk.Label(convert_frame, text="Из валюты:").grid(row=0, column=2, sticky="e", padx=5, pady=10)
        self.from_currency_var = tk.StringVar(value="USD")
        self.from_currency_combo = ttk.Combobox(convert_frame, textvariable=self.from_currency_var, 
                                                 values=CURRENCIES, width=8, font=("Arial", 11))
        self.from_currency_combo.grid(row=0, column=3, padx=5, pady=10)

        # В валюту
        tk.Label(convert_frame, text="В валюту:").grid(row=0, column=4, sticky="e", padx=5, pady=10)
        self.to_currency_var = tk.StringVar(value="EUR")
        self.to_currency_combo = ttk.Combobox(convert_frame, textvariable=self.to_currency_var, 
                                               values=CURRENCIES, width=8, font=("Arial", 11))
        self.to_currency_combo.grid(row=0, column=5, padx=5, pady=10)

        # Кнопка конвертации
        self.convert_btn = tk.Button(convert_frame, text="💱 Конвертировать", command=self.convert_currency,
                                      bg="lightblue", font=("Arial", 11))
        self.convert_btn.grid(row=0, column=6, padx=15, pady=10)

        # === Результат ===
        result_frame = tk.LabelFrame(self.root, text="Результат", padx=15, pady=10)
        result_frame.pack(fill="x", padx=10, pady=5)

        self.result_label = tk.Label(result_frame, text="", font=("Arial", 14, "bold"), fg="darkgreen")
        self.result_label.pack(pady=10)

        # Курс
        self.rate_label = tk.Label(result_frame, text="", font=("Arial", 10), fg="gray")
        self.rate_label.pack()

        # === Таблица истории ===
        history_frame = tk.LabelFrame(self.root, text="История конвертаций", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата и время", "Исходная сумма", "Из", "В", "Результат", "Курс")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        self.tree.heading("Дата и время", text="Дата и время")
        self.tree.heading("Исходная сумма", text="Исходная сумма")
        self.tree.heading("Из", text="Из")
        self.tree.heading("В", text="В")
        self.tree.heading("Результат", text="Результат")
        self.tree.heading("Курс", text="Курс")

        self.tree.column("Дата и время", width=130)
        self.tree.column("Исходная сумма", width=90)
        self.tree.column("Из", width=50)
        self.tree.column("В", width=50)
        self.tree.column("Результат", width=100)
        self.tree.column("Курс", width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="💾 Сохранить историю", command=self.save_history,
                  bg="lightyellow", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить историю", command=self.load_history_interactive,
                  bg="lightyellow", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history,
                  bg="salmon", width=15).pack(side="left", padx=5)

        # Статус
        self.status_label = tk.Label(btn_frame, text="Готов к работе", font=("Arial", 9), fg="blue")
        self.status_label.pack(side="right", padx=10)

    def get_exchange_rate(self, from_currency, to_currency):
        """Получение курса обмена через API"""
        try:
            url = f"{API_URL}{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success" or "rates" in data:
                rates = data.get("conversion_rates", data.get("rates", {}))
                rate = rates.get(to_currency)
                if rate:
                    return rate
                else:
                    messagebox.showerror("Ошибка", f"Валюта {to_currency} не найдена")
                    return None
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курсы валют")
                return None
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API: {e}")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Неверный ответ от сервера")
            return None

    def convert_currency(self):
        amount_str = self.amount_entry.get().strip()
        from_currency = self.from_currency_var.get().upper()
        to_currency = self.to_currency_var.get().upper()

        # Валидация суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом")
            return

        # Обновляем статус
        self.status_label.config(text="Загрузка курсов...", fg="orange")
        self.root.update()

        # Получаем курс
        rate = self.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            self.status_label.config(text="Ошибка получения курса", fg="red")
            return

        # Вычисляем результат
        result = amount * rate

        # Обновляем отображение
        self.result_label.config(text=f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")
        self.rate_label.config(text=f"Курс: 1 {from_currency} = {rate:.4f} {to_currency}")
        self.status_label.config(text="Конвертация выполнена", fg="green")

        # Добавляем в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "result": result,
            "rate": rate
        }
        
        self.history.insert(0, history_entry)
        
        # Ограничиваем историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[:50]
        
        self.refresh_history_table()
        messagebox.showinfo("Успех", f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")

    def refresh_history_table(self, history_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = history_to_show if history_to_show is not None else self.history
        for record in data:
            self.tree.insert("", tk.END, values=(
                record["timestamp"],
                f"{record['amount']:.2f}",
                record["from_currency"],
                record["to_currency"],
                f"{record['result']:.2f}",
                f"{record['rate']:.4f}"
            ))

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"История сохранена в {HISTORY_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.history = []

    def load_history_interactive(self):
        self.load_history()
        self.refresh_history_table()
        messagebox.showinfo("Загрузка", f"Загружено записей в истории: {len(self.history)}")

    def clear_history(self):
        if messagebox.askyesno("Очистка", "Вы уверены, что хотите очистить всю историю конвертаций?"):
            self.history = []
            self.refresh_history_table()
            messagebox.showinfo("Очистка", "История очищена")


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
  
