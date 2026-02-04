import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import subprocess
import time
import qrcode
import sys
import threading
import os

# Configuration
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"
TARGET_PORT = 8080

def start_ngrok():
    """Starts ngrok in a subprocess if not already running."""
    try:
        # Check if already running
        requests.get(NGROK_API_URL, timeout=1)
        print("Existing ngrok instance found.")
        return None
    except requests.ConnectionError:
        print("Starting ngrok...")
        # Start ngrok, silencing output to avoid console clutter if possible
        # startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(["ngrok", "http", str(TARGET_PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return process

def get_public_url(retries=10):
    """Polls ngrok API to get the public URL."""
    for _ in range(retries):
        try:
            response = requests.get(NGROK_API_URL)
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                # Prefer https
                for tunnel in tunnels:
                    if tunnel['proto'] == 'https':
                        return tunnel['public_url']
                return tunnels[0]['public_url']
        except Exception:
            pass
        time.sleep(1)
    return None

def show_qr(url):
    root = tk.Tk()
    root.title("AbletonOSC Remote Access")
    root.geometry("400x520")
    root.configure(bg="#1e1e1e")

    # Generate QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img_data = qr.make_image(fill_color="black", back_color="white")
    
    # Convert for Tkinter
    img = ImageTk.PhotoImage(img_data)

    lbl_title = tk.Label(root, text="Scan to Control Live", font=("Helvetica", 16, "bold"), fg="white", bg="#1e1e1e")
    lbl_title.pack(pady=20)

    lbl_img = tk.Label(root, image=img, bg="#1e1e1e")
    lbl_img.image = img # Keep reference
    lbl_img.pack()

    # URL Entry (Copyable)
    entry_url = tk.Entry(root, font=("Consolas", 10), fg="#00ff00", bg="#2d2d2d", justify="center", bd=0, relief="flat")
    entry_url.insert(0, url)
    entry_url.configure(state="readonly", readonlybackground="#2d2d2d")
    entry_url.pack(pady=20, fill="x", padx=40, ipady=8)

    lbl_note = tk.Label(root, text="Keep this window open to maintain connection.", fg="#aaaaaa", bg="#1e1e1e")
    lbl_note.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    ngrok_proc = start_ngrok()
    
    print("Waiting for tunnel...")
    public_url = get_public_url()
    
    if public_url:
        print(f"Tunnel established: {public_url}")
        try:
            show_qr(public_url)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to establish tunnel.")
        # If we failed and started a process, kill it
        if ngrok_proc:
            ngrok_proc.terminate()
            
    # Cleanup on exit
    if ngrok_proc:
        print("Stopping ngrok...")
        ngrok_proc.terminate()
