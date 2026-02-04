import tkinter as tk
from PIL import Image, ImageTk
import socket
import qrcode
import sys

# Configuration
PORT = 8080

def get_local_ip():
    """Detects the local IP address connected to the network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public DNS server (doesn't actually send data) to determine outgoing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def show_qr(url, ip):
    root = tk.Tk()
    root.title(f"AbletonOSC - WiFi: {ip}")
    root.geometry("400x520")
    root.configure(bg="#1e1e1e")

    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img_data = qr.make_image(fill_color="black", back_color="white")
    img = ImageTk.PhotoImage(img_data)

    # UI
    lbl_title = tk.Label(root, text="WiFi Connection", font=("Helvetica", 16, "bold"), fg="#00ccff", bg="#1e1e1e")
    lbl_title.pack(fill="x", pady=(0, 20), ipady=10)

    lbl_img = tk.Label(root, image=img, bg="#1e1e1e")
    lbl_img.image = img
    lbl_img.pack()

    # URL Entry (Copyable)
    # Using Entry instead of Label allows text selection/copying
    entry_url = tk.Entry(root, font=("Consolas", 12, "bold"), fg="#00ccff", bg="#2d2d2d", justify="center", bd=0, relief="flat")
    entry_url.insert(0, url)
    entry_url.configure(state="readonly", readonlybackground="#2d2d2d") # Readonly but selectable
    entry_url.pack(pady=20, fill="x", padx=40, ipady=8)

    # Footer info
    lbl_hostname = tk.Label(root, text=f"Host: {socket.gethostname()}", fg="#aaaaaa", bg="#1e1e1e")
    lbl_hostname.pack(side="bottom", pady=2)
    
    lbl_note = tk.Label(root, text="Connect your mobile to the SAME WiFi.", fg="#aaaaaa", bg="#1e1e1e")
    lbl_note.pack(side="bottom", pady=5)

    root.mainloop()

if __name__ == "__main__":
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}"
    print(f"Detected IP: {local_ip}")
    print(f"URL: {url}")
    
    show_qr(url, local_ip)
