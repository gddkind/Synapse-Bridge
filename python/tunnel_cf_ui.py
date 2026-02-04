import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import threading
import qrcode
import re
import sys
import os
import signal

# Configuration
TARGET_PORT = 8080
CLOUDFLARED_CMD = ["cloudflared", "tunnel", "--url", f"http://localhost:{TARGET_PORT}"]

class CloudflareTunnelUI:
    def __init__(self):
        self.process = None
        self.public_url = None
        self.root = None
        self.stop_event = threading.Event()

    def start_tunnel(self):
        """Starts cloudflared and monitors output for the URL."""
        # Create a startupinfo object to hide the console window of the subprocess
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        try:
            self.process = subprocess.Popen(
                CLOUDFLARED_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo
            )
            
            # Start a thread to read stderr (where cloudflared usually prints the URL)
            thread = threading.Thread(target=self._monitor_output, daemon=True)
            thread.start()
            
        except FileNotFoundError:
            messagebox.showerror("Error", "cloudflared not found in PATH.\nPlease install Cloudflare Tunnel.")
            sys.exit(1)

    def _monitor_output(self):
        """Reads stderr looking for the trycloudflare.com URL."""
        url_pattern = re.compile(r"https://[-a-zA-Z0-9]+\.trycloudflare\.com")
        
        while not self.stop_event.is_set() and self.process.poll() is None:
            line = self.process.stderr.readline()
            if not line:
                break
            
            print(f"[cloudflared] {line.strip()}") # Optional: debug output
            
            match = url_pattern.search(line)
            if match:
                self.public_url = match.group(0)
                print(f"URL Found: {self.public_url}")
                # Schedule the UI update on the main thread
                if self.root:
                    self.root.after(0, self._show_qr_content)
                return

    def _show_qr_content(self):
        """Updates the Tkinter window with the QR code."""
        if not self.public_url:
            return

        # Clear loading text
        for widget in self.root.winfo_children():
            widget.destroy()

        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(self.public_url)
        qr.make(fit=True)
        img_data = qr.make_image(fill_color="black", back_color="white")
        img = ImageTk.PhotoImage(img_data)

        # UI Elements
        lbl_title = tk.Label(self.root, text="Cloudflare Tunnel Active", font=("Helvetica", 16, "bold"), fg="white", bg="#f38020") # Cloudflare Orange
        lbl_title.pack(fill="x", pady=(0, 20), ipady=10)

        lbl_img = tk.Label(self.root, image=img, bg="#1e1e1e")
        lbl_img.image = img
        lbl_img.pack()

        # URL Entry (Copyable)
        entry_url = tk.Entry(self.root, font=("Consolas", 10), fg="#f38020", bg="#2d2d2d", justify="center", bd=0, relief="flat")
        entry_url.insert(0, self.public_url)
        entry_url.configure(state="readonly", readonlybackground="#2d2d2d")
        entry_url.pack(pady=20, fill="x", padx=40, ipady=8)

        lbl_note = tk.Label(self.root, text="Scan to control. Close this window to stop tunnel.", fg="#aaaaaa", bg="#1e1e1e")
        lbl_note.pack(side="bottom", pady=10)

    def run(self):
        self.root = tk.Tk()
        self.root.title("AbletonOSC - Cloudflare")
        self.root.geometry("400x550")
        self.root.configure(bg="#1e1e1e")

        # Initial 'Loading' state
        lbl_loading = tk.Label(self.root, text="Starting Cloudflare Tunnel...", font=("Helvetica", 12), fg="white", bg="#1e1e1e")
        lbl_loading.pack(expand=True)

        self.start_tunnel()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.root.mainloop()

    def cleanup(self):
        print("Stopping tunnel...")
        self.stop_event.set()
        if self.process:
            self.process.terminate()
        if self.root:
            self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = CloudflareTunnelUI()
    app.run()
