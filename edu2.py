import pyperclip
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import google.generativeai as genai
from dotenv import load_dotenv
import os
import google.generativeai as genai

# PLACE GEMINI API KEY IN SINGLE QUOTES
API_KEY = 'YOUR_API_KEY'

genai.configure(
    api_key=API_KEY
)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

previous_clipboard_content = ""

def clear_clipboard():
    pyperclip.copy("")

def copy_highlighted_text_to_txt(file_path):
    try:
        highlighted_text = pyperclip.paste()
        with open(file_path, 'a') as txt_file:
            txt_file.write(highlighted_text + "\n")
        print("Highlighted text copied to", file_path)
    except Exception as e:
        print("Error:", e)

def browse_file():
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    file_path.set(filename)

def open_file():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"),("Word files", "*.doc")])
    if filename:
        with open(filename, 'r') as file:
            content = file.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, content)

def copy_highlighted_text():
    highlighted_text = pyperclip.paste()
    current_text = text_widget.get("1.0", tk.END)
    updated_text = f"{current_text}{highlighted_text}\n"
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, updated_text)
    text_widget.see(tk.END)

def check_clipboard_once():
    global previous_clipboard_content
    clipboard_content = pyperclip.paste()
    if clipboard_content != previous_clipboard_content:
        previous_clipboard_content = clipboard_content
        if file_path.get():
            copy_highlighted_text_to_txt(file_path.get())
        copy_highlighted_text()
    root.after(1000, check_clipboard_once)

def show_warning_window():
    warning_window = tk.Toplevel(root)
    warning_window.title("Warning")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    warning_x = (screen_width - 300) // 2
    warning_y = (screen_height - 100) // 2
    warning_window.geometry("300x100+{}+{}".format(warning_x, warning_y))
    warning_window.resizable(False, False)
    warning_label = tk.Label(warning_window, text="Before starting, make sure to save first", font=("Arial", 12))
    warning_label.pack(pady=10)
    cancel_button = tk.Button(warning_window, text="I understand", command=warning_window.destroy)
    cancel_button.pack(side="right", padx=10)
    warning_window.wait_window(warning_window)

def close_warning_window(root, warning_window):
    warning_window.destroy()
    root.deiconify()

def open_warning_window():
    show_warning_window

def generate_response_from_gemini():
    context = text_widget.get("1.0", tk.END)
    question = question_entry.get()
    context += "\n" + question

    def generate_response():
        response = chat.send_message(context)
        ai_text_widget.config(state=tk.NORMAL)
        ai_text_widget.insert(tk.END, response.text + "\n")
        ai_text_widget.config(state=tk.DISABLED)

    threading.Thread(target=generate_response).start()

def save_ai_text():
    try:
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"),("Word files", "*.doc")])
        if filename:
            with open(filename, 'w') as file:
                ai_text_content = ai_text_widget.get("1.0", tk.END)
                file.write(ai_text_content)
            messagebox.showinfo("Success", "AI text saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving AI text: {e}")

root = tk.Tk()
root.title("GlowSpotter")
root.iconbitmap("logo.ico")
root.configure(background="#4E4E4E")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 1050) // 2
y = (screen_height - 600) // 2
root.geometry("1050x600+{}+{}".format(x, y))

root.resizable(False,False)

file_path = tk.StringVar()
file_entry = tk.Entry(root, textvariable=file_path, width=30)
file_entry.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
browse_button = tk.Button(root, text="Save", command=browse_file)
browse_button.grid(row=0, column=0, padx=200, pady=(10, 5), sticky="w")
open_file_button = tk.Button(root, text="Open", command=open_file)
open_file_button.grid(row=0, column=0, padx=240, pady=(10, 5), sticky="w")

text_widget = tk.Text(root, height=20, width=70)
text_widget.grid(row=1, column=0, rowspan=4, padx=(10, 0), pady=(0, 0), sticky="nsew")

scrollbar_text = tk.Scrollbar(root, orient="vertical", command=text_widget.yview)
scrollbar_text.grid(row=1, column=1, rowspan=4,padx=(10, 10), pady=(0, 0), sticky="ns")
text_widget.config(yscrollcommand=scrollbar_text.set)

ai_text_widget = tk.Text(root, height=20, width=70)
ai_text_widget.grid(row=1, column=4, rowspan=4, padx=10, pady=(0, 0), sticky="nesw")

scrollbar_ai_text = tk.Scrollbar(root, orient="vertical", command=ai_text_widget.yview)
scrollbar_ai_text.grid(row=1, column=3, rowspan=4, pady=(0,0), sticky="ns")
ai_text_widget.config(yscrollcommand=scrollbar_ai_text.set)

question_entry = tk.Entry(root, width=70)
question_entry.grid(row=5, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="ew")

save_ai_button = tk.Button(root, text="Save AI Text", command=save_ai_text)
save_ai_button.grid(row=5, column=4, padx=150, pady=(0, 0), sticky="w")

gemini_button = tk.Button(root, text="Get Gemini AI Response", command=generate_response_from_gemini)
gemini_button.grid(row=5, column=4, columnspan=1, padx=10, pady=(0, 0), sticky="w")

for i in range(6):
    root.grid_rowconfigure(i, weight=1)

for i in range(6):
    root.grid_columnconfigure(i, weight=1)

check_clipboard_once()
show_warning_window()

root.mainloop()
