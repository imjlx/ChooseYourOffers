import tkinter as tk
from tkinter import ttk

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("虚线分割线示例")
        self.geometry("400x300")

        self.create_separator()

    def create_separator(self):
        separator = ttk.Separator(self, orient='horizontal', style='Dashed.TSeparator')
        separator.pack(fill='x', padx=5, pady=5)

app = GUI()
app.mainloop()