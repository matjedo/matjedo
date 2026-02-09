import json
import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font as tkFont

WEBHOOK_FILE = "webhooks.json"

# ------------------- JSON -------------------
def ensure_webhook_file():
    if not os.path.exists(WEBHOOK_FILE):
        with open(WEBHOOK_FILE, "w") as f:
            json.dump([], f)
    else:
        try:
            with open(WEBHOOK_FILE, "r") as f:
                data = f.read().strip()
                if not data:
                    with open(WEBHOOK_FILE, "w") as f2:
                        json.dump([], f2)
        except json.JSONDecodeError:
            with open(WEBHOOK_FILE, "w") as f:
                json.dump([], f)

def load_webhooks():
    ensure_webhook_file()
    with open(WEBHOOK_FILE, "r") as f:
        data = json.load(f)
    # Atualiza webhooks antigas sem nome
    updated = False
    for wh in data:
        if isinstance(wh, str):
            # Pergunta nome
            name = simpledialog.askstring("Webhook sem nome", f"Digite um nome para webhook:\n{wh}")
            if not name:
                name = wh
            idx = data.index(wh)
            data[idx] = {"url": wh, "name": name}
            updated = True
    if updated:
        save_webhooks(data)
    return data

def save_webhooks(webhooks):
    with open(WEBHOOK_FILE, "w") as f:
        json.dump(webhooks, f, indent=4)

# ------------------- Funções principais -------------------
def add_webhook():
    url = simpledialog.askstring("Adicionar Webhook", "Digite a URL do webhook:")
    if not url:
        return
    name = simpledialog.askstring("Nome da Webhook", "Digite um nome para essa webhook:")
    if not name:
        name = url
    webhooks = load_webhooks()
    if any(wh["url"] == url for wh in webhooks):
        messagebox.showinfo("Info", "Webhook já existe!")
        return
    webhooks.append({"url": url, "name": name})
    save_webhooks(webhooks)
    refresh_webhook_list()

def remove_webhook():
    selected = listbox_webhooks.curselection()
    if not selected:
        messagebox.showinfo("Info", "Selecione uma webhook para remover")
        return
    index = selected[0]
    webhooks = load_webhooks()
    removed = webhooks.pop(index)
    save_webhooks(webhooks)
    refresh_webhook_list()
    messagebox.showinfo("Info", f"Webhook removida: {removed['name']}")

def refresh_webhook_list():
    listbox_webhooks.delete(0, tk.END)
    for wh in load_webhooks():
        listbox_webhooks.insert(tk.END, wh["name"])

def send_message():
    selected = listbox_webhooks.curselection()
    if not selected:
        messagebox.showinfo("Info", "Selecione uma webhook para enviar mensagem")
        return
    webhook = load_webhooks()[selected[0]]
    url = webhook["url"]
    content = text_message.get("1.0", tk.END).strip()
    file_path = entry_file.get().strip() or None

    if not content and not file_path:
        messagebox.showinfo("Info", "Digite uma mensagem ou selecione um arquivo")
        return

    data = {"content": content}
    files = None

    if file_path:
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return
        files = {"file": open(file_path, "rb")}

    try:
        response = requests.post(url, data=data, files=files)
        if files:
            files["file"].close()
        if response.status_code in [200, 204]:
            messagebox.showinfo("Sucesso", "Mensagem enviada!")
        else:
            messagebox.showerror("Erro", f"Falha ao enviar: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def select_file():
    filename = filedialog.askopenfilename(title="Selecione um arquivo")
    if filename:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filename)

def insert_emoji(emoji):
    text_message.insert(tk.END, emoji)

# ------------------- Lista de Emojis -------------------
emojis = ["😀","😂","😎","🔥","💀","✅","❌","🚨","🎉","❤️"]

# ------------------- GUI -------------------
root = tk.Tk()
root.title("Webhook Manager GUI - Round Buttons")
root.geometry("850x550")
root.configure(bg="#2e2e2e")  # Fundo escuro

# Fontes
font_label = tkFont.Font(family="Helvetica", size=12, weight="bold")
font_button = tkFont.Font(family="Helvetica", size=10, weight="bold")
font_text = tkFont.Font(family="Consolas", size=11)

# --- Frame Webhooks ---
frame_left = tk.Frame(root, bg="#2e2e2e")
frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

tk.Label(frame_left, text="Webhooks", font=font_label, fg="white", bg="#2e2e2e").pack(pady=5)

listbox_webhooks = tk.Listbox(frame_left, width=50, font=font_text, bg="#1e1e1e", fg="white", selectbackground="#4CAF50", selectforeground="white")
listbox_webhooks.pack(fill=tk.Y, expand=True)

scroll_webhooks = tk.Scrollbar(frame_left)
scroll_webhooks.pack(side=tk.RIGHT, fill=tk.Y)
listbox_webhooks.config(yscrollcommand=scroll_webhooks.set)
scroll_webhooks.config(command=listbox_webhooks.yview)

def create_rounded_button(parent, text, bg, fg, command):
    return tk.Button(parent, text=text, bg=bg, fg=fg, font=font_button, command=command, relief="flat", bd=0, highlightthickness=0, padx=10, pady=5)

btn_add = create_rounded_button(frame_left, "Adicionar Webhook", "#4CAF50", "white", add_webhook)
btn_add.pack(pady=5, fill=tk.X)

btn_remove = create_rounded_button(frame_left, "Remover Webhook", "#f44336", "white", remove_webhook)
btn_remove.pack(pady=5, fill=tk.X)

refresh_webhook_list()

# --- Frame Mensagem e Envio ---
frame_right = tk.Frame(root, bg="#2e2e2e")
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

tk.Label(frame_right, text="Mensagem", font=font_label, fg="white", bg="#2e2e2e").pack(pady=5)
text_message = tk.Text(frame_right, height=10, font=font_text, bg="#1e1e1e", fg="white", insertbackground="white")
text_message.pack(fill=tk.X)

# Emojis como texto
frame_emojis = tk.Frame(frame_right, bg="#2e2e2e")
frame_emojis.pack(pady=5, fill=tk.X)
tk.Label(frame_emojis, text="Emojis: ", font=font_label, fg="white", bg="#2e2e2e").pack(side=tk.LEFT)

for em in emojis:
    btn = create_rounded_button(frame_emojis, em, "#555555", "white", lambda e=em: insert_emoji(e))
    btn.pack(side=tk.LEFT, padx=2)

# Arquivo
frame_file = tk.Frame(frame_right, bg="#2e2e2e")
frame_file.pack(pady=5, fill=tk.X)
entry_file = tk.Entry(frame_file, font=font_text, bg="#1e1e1e", fg="white", insertbackground="white")
entry_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
btn_file = create_rounded_button(frame_file, "Selecionar arquivo", "#2196F3", "white", select_file)
btn_file.pack(side=tk.RIGHT)

# Botão enviar
btn_send = create_rounded_button(frame_right, "Enviar Mensagem", "#4CAF50", "white", send_message)
btn_send.pack(pady=10, fill=tk.X)

root.mainloop()
