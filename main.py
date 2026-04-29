import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Баскаков Арсений")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a2e')
        
        # Предопределённые задачи
        self.predefined_tasks = [
            ("Решить 5 уравнений по математике", "учёба"),
            ("Сделать 20 приседаний", "спорт"),
            ("Написать код на Python", "работа"),
            ("Выпить стакан воды", "спорт"),
            ("Прочитать параграф по истории", "учёба"),
            ("Составить план на завтра", "работа"),
            ("Убраться в комнате", "работа"),
            ("Пробежать 1.5 км", "спорт"),
            ("Выучить 15 английских слов", "учёба"),
            ("Сделать зарядку 10 минут", "спорт"),
            ("Повторить пройденный материал", "учёба"),
            ("Помочь родителям", "работа")
        ]
        
        self.task_types = ["учёба", "спорт", "работа", "все"]
        self.filter_type = tk.StringVar(value="все")
        
        # Загружаем историю
        self.history = self.load_history()
        
        self.create_widgets()
        self.display_history()
        self.update_stats()
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="🎲 Random Task Generator", 
                                font=('Arial', 18, 'bold'), bg='#1a1a2e', fg='#e94560')
        title_label.pack(pady=15)
        
        # --- Рамка генерации ---
        frame_gen = tk.LabelFrame(self.root, text="🎯 Генератор задач", 
                                   font=('Arial', 12, 'bold'), bg='#16213e', 
                                   fg='#ffffff', padx=10, pady=10)
        frame_gen.pack(fill="x", padx=15, pady=5)
        
        self.gen_button = tk.Button(frame_gen, text="✨ Сгенерировать случайную задачу ✨",
                                     command=self.generate_task,
                                     bg='#e94560', fg='white', font=('Arial', 11, 'bold'),
                                     padx=10, pady=8, cursor='hand2', relief='raised')
        self.gen_button.pack(pady=8)
        
        self.current_task_label = tk.Label(frame_gen, text="", font=('Arial', 12, 'bold'),
                                            fg='#00d4ff', bg='#16213e', wraplength=550)
        self.current_task_label.pack(pady=8)
        
        # --- Рамка добавления ---
        frame_add = tk.LabelFrame(self.root, text="➕ Добавить свою задачу",
                                   font=('Arial', 12, 'bold'), bg='#16213e',
                                   fg='#ffffff', padx=10, pady=10)
        frame_add.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_add, text="Название задачи:", bg='#16213e', font=('Arial', 10), fg='white').grid(row=0, column=0, padx=8, pady=8, sticky='e')
        self.new_task_entry = tk.Entry(frame_add, width=40, font=('Arial', 10), relief='solid', borderwidth=1, bg='#0f3460', fg='white', insertbackground='white')
        self.new_task_entry.grid(row=0, column=1, padx=8, pady=8)
        
        tk.Label(frame_add, text="Тип задачи:", bg='#16213e', font=('Arial', 10), fg='white').grid(row=1, column=0, padx=8, pady=8, sticky='e')
        self.new_type_combo = ttk.Combobox(frame_add, values=self.task_types[:-1],
                                            state="readonly", width=37, font=('Arial', 10))
        self.new_type_combo.current(0)
        self.new_type_combo.grid(row=1, column=1, padx=8, pady=8)
        
        self.add_button = tk.Button(frame_add, text="📌 Добавить задачу", command=self.add_task,
                                     bg='#00b4d8', fg='white', font=('Arial', 10, 'bold'),
                                     padx=10, pady=4, cursor='hand2')
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # --- Рамка фильтрации ---
        frame_filter = tk.LabelFrame(self.root, text="🔍 Фильтрация",
                                      font=('Arial', 12, 'bold'), bg='#16213e',
                                      fg='#ffffff', padx=10, pady=10)
        frame_filter.pack(fill="x", padx=15, pady=5)
        
        for t in self.task_types:
            rb = tk.Radiobutton(frame_filter, text=t.capitalize(), variable=self.filter_type,
                                value=t, command=self.display_history, bg='#16213e',
                                font=('Arial', 11), selectcolor='#16213e', fg='white')
            rb.pack(side="left", padx=20)
        
        # --- Рамка истории ---
        frame_history = tk.LabelFrame(self.root, text="📜 История задач",
                                       font=('Arial', 12, 'bold'), bg='#16213e',
                                       fg='#ffffff', padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=15, pady=5)
        
        list_frame = tk.Frame(frame_history, bg='#16213e')
        list_frame.pack(fill="both", expand=True)
        
        self.history_listbox = tk.Listbox(list_frame, height=13, font=('Arial', 10),
                                           selectmode=tk.SINGLE, bg='#0f3460', fg='white',
                                           relief='solid', borderwidth=1, selectbackground='#e94560')
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview, bg='#16213e')
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Нижняя панель ---
        bottom_frame = tk.Frame(self.root, bg='#1a1a2e')
        bottom_frame.pack(fill="x", padx=15, pady=10)
        
        self.save_button = tk.Button(bottom_frame, text="💾 Сохранить историю в JSON", 
                                      command=self.save_history_to_json,
                                      bg='#f4a261', fg='white', font=('Arial', 10, 'bold'),
                                      padx=10, pady=5, cursor='hand2')
        self.save_button.pack(side="left", padx=5)
        
        self.stats_label = tk.Label(bottom_frame, text="", bg='#1a1a2e', font=('Arial', 10, 'italic'), fg='#e9c46a')
        self.stats_label.pack(side="right", padx=5)
    
    def update_stats(self):
        total = len(self.history)
        self.stats_label.config(text=f"📊 Всего задач: {total}")
    
    def generate_task(self):
        task, task_type = random.choice(self.predefined_tasks)
        self.history.append({"task": task, "type": task_type})
        self.current_task_label.config(text=f"🎉 {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_stats()
    
    def add_task(self):
        task = self.new_task_entry.get().strip()
        task_type = self.new_type_combo.get()
        
        # Валидация
        if not task:
            messagebox.showerror("Ошибка!", "❌ Название задачи не может быть пустым!")
            return
        
        if len(task) < 2:
            messagebox.showerror("Ошибка!", "❌ Название слишком короткое (минимум 2 символа)!")
            return
        
        if len(task) > 80:
            messagebox.showerror("Ошибка!", "❌ Название слишком длинное (максимум 80 символов)!")
            return
        
        self.predefined_tasks.append((task, task_type))
        self.history.append({"task": task, "type": task_type})
        
        self.new_task_entry.delete(0, tk.END)
        self.current_task_label.config(text=f"✅ Добавлено: {task} [{task_type}]")
        self.display_history()
        self.save_history_to_json()
        self.update_stats()
        
        messagebox.showinfo("Успех!", f"✅ Задача '{task}' успешно добавлена!")
    
    def display_history(self):
        self.history_listbox.delete(0, tk.END)
        current_filter = self.filter_type.get()
        
        if not self.history:
            self.history_listbox.insert(tk.END, "📭 История пуста. Нажмите 'Сгенерировать' или 'Добавить'")
            self.history_listbox.itemconfig(0, fg='#e94560')
            return
        
        filtered = [item for item in self.history if current_filter == "все" or item["type"] == current_filter]
        
        if not filtered:
            self.history_listbox.insert(tk.END, f"📭 Нет задач типа '{current_filter}'")
            self.history_listbox.itemconfig(0, fg='#e94560')
            return
        
        for i, item in enumerate(filtered, 1):
            display_text = f"{i:2d}. {item['task']} — [{item['type']}]"
            self.history_listbox.insert(tk.END, display_text)
    
    def load_history(self):
        if not os.path.exists("tasks.json"):
            return []
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_history_to_json(self):
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Сохранено", "✅ История успешно сохранена в tasks.json!")
        except IOError:
            messagebox.showerror("Ошибка", "❌ Не удалось сохранить историю!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
  
