import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import queue
import socket
import qrcode
from PIL import Image, ImageTk
import mido
from pythonosc import udp_client
import sys
import os
import re

# Configuração
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")
OSC_IP = "127.0.0.1"
OSC_PORT = 1337

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AbletonOSC Dashboard")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")
        
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TButton", background="#333", foreground="white", borderwidth=1)
        style.map("TButton", background=[("active", "#555")])
        style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
        
        # Variáveis de Estado
        self.server_process = None
        self.log_queue = queue.Queue()
        self.osc_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
        
        # Variáveis de Filtro
        self.show_osc_js = tk.BooleanVar(value=True)
        self.show_osc_in = tk.BooleanVar(value=True)
        self.show_midi = tk.BooleanVar(value=True)
        self.show_clock = tk.BooleanVar(value=False) # Clock é muito ruidoso
        self.show_transport = tk.BooleanVar(value=True)
        self.show_errors = tk.BooleanVar(value=True)
        
        # === LAYOUT ===
        
        # 1. Top Bar (Status + QR + Launch)
        self.top_frame = tk.Frame(root, bg="#252526", height=150)
        self.top_frame.pack(fill="x", side="top")
        
        self.setup_qr_section()
        
        # Launch Button Frame (Right side)
        media_frame = tk.Frame(self.top_frame, bg="#252526")
        media_frame.pack(side="right", padx=20, pady=20)
        
        btn_launch = tk.Button(media_frame, text="LAUNCH INTERFACE", command=self.launch_osc, 
                               bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"), height=2, width=20)
        btn_launch.pack()
        
        # 2. Control Bar (MIDI)
        self.control_frame = tk.Frame(root, bg="#333333", height=80)
        self.control_frame.pack(fill="x", side="top", pady=2)
        
        self.setup_midi_section()
        
        # 3. Log Section
        self.log_frame = tk.Frame(root, bg="#1e1e1e")
        self.log_frame.pack(fill="both", expand=True, side="bottom", padx=5, pady=5)
        
        self.setup_log_section()
        
        # Iniciar Servidor
        self.start_server()
        
        # Loop de verificação da fila de logs
        self.root.after(100, self.process_log_queue)

    def setup_qr_section(self):
        # IP info
        local_ip = self.get_local_ip()
        url = f"http://{local_ip}:8080"
        
        info_frame = tk.Frame(self.top_frame, bg="#252526")
        info_frame.pack(side="left", padx=20, pady=10)
        
        tk.Label(info_frame, text="AbletonOSC Server", font=("Segoe UI", 18, "bold"), bg="#252526", fg="#007acc").pack(anchor="w")
        tk.Label(info_frame, text=f"Connect via WiFi: {url}", font=("Consolas", 12), bg="#252526", fg="#4CAF50").pack(anchor="w", pady=5)
        
        # QR Code
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img_data = qr.make_image(fill_color="white", back_color="#252526")
        self.qr_img = ImageTk.PhotoImage(img_data)
        
        qr_label = tk.Label(self.top_frame, image=self.qr_img, bg="#252526")
        qr_label.pack(side="right", padx=20, pady=10)

    def setup_midi_section(self):
        # Conteúdo MIDI
        midi_lbl = tk.Label(self.control_frame, text="MIDI Settings", font=("Segoe UI", 12, "bold"), bg="#333333", fg="white")
        midi_lbl.pack(side="left", padx=10)
        
        # Outputs
        tk.Label(self.control_frame, text="Out (To Live):", bg="#333333", fg="#aaa").pack(side="left", padx=5)
        self.box_out = ttk.Combobox(self.control_frame, values=mido.get_output_names(), width=25)
        if self.box_out['values']: self.box_out.current(0)
        self.box_out.pack(side="left", padx=5)
        
        # Inputs
        tk.Label(self.control_frame, text="In (Feedback):", bg="#333333", fg="#aaa").pack(side="left", padx=5)
        self.box_in = ttk.Combobox(self.control_frame, values=mido.get_input_names(), width=25)
        if self.box_in['values']: self.box_in.current(0)
        self.box_in.pack(side="left", padx=5)
        
        btn_apply = tk.Button(self.control_frame, text="Apply MIDI", command=self.apply_midi, bg="#007acc", fg="white", font=("Segoe UI", 9, "bold"))
        btn_apply.pack(side="left", padx=15)
        
        # Refresh btn
        btn_refresh = tk.Button(self.control_frame, text="↻", command=self.refresh_midi_list, bg="#444", fg="white")
        btn_refresh.pack(side="left")

    def setup_log_section(self):
        # Barra de Filtros
        filter_bar = tk.Frame(self.log_frame, bg="#1e1e1e")
        filter_bar.pack(fill="x", side="top", pady=5)
        
        tk.Label(filter_bar, text="Filters:", bg="#1e1e1e", fg="#aaa").pack(side="left", padx=5)
        
        filters = [
            ("JS Log", self.show_osc_js),
            ("OSC In", self.show_osc_in),
            ("MIDI", self.show_midi),
            ("Clock (Noise)", self.show_clock),
            ("Transport", self.show_transport),
            ("Errors", self.show_errors)
        ]
        
        for text, var in filters:
            cb = ttk.Checkbutton(filter_bar, text=text, variable=var)
            cb.pack(side="left", padx=5)
            
        btn_clear = tk.Button(filter_bar, text="Clear Log", command=self.clear_log, bg="#444", fg="white")
        btn_clear.pack(side="right", padx=10)

        # Console
        self.console = scrolledtext.ScrolledText(self.log_frame, bg="#000", fg="#ddd", font=("Consolas", 10), state="disabled")
        self.console.pack(fill="both", expand=True)
        
        # Tags de Cores
        self.console.tag_config("ERROR", foreground="#ff4444")
        self.console.tag_config("OSC-JS", foreground="#fabd2f") # Amarelo
        self.console.tag_config("OSC-IN", foreground="#8ec07c") # Verde
        self.console.tag_config("MIDI", foreground="#d3869b") # Roxo
        self.console.tag_config("INFO", foreground="#83a598") # Azul
        self.console.tag_config("DIM", foreground="#666666") # Cinza escuro

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def launch_osc(self):
        """Lança o Open Stage Control com as configurações corretas"""
        # Lista de locais possíveis para o executável
        possible_paths = [
            r"C:\osc\open-stage-control.exe",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "osc", "open-stage-control.exe"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Installers", "open-stage-control", "open-stage-control.exe")
        ]

        osc_exe = None
        for path in possible_paths:
            if os.path.exists(path):
                osc_exe = path
                break

        if not osc_exe:
            self.log_manual("Open Stage Control executable not found!", "ERROR")
            tk.messagebox.showerror(
                "Erro de Configuração", 
                "Não foi possível encontrar o 'open-stage-control.exe'.\n\n"
                "Por favor, certifique-se de ter extraído o arquivo ZIP da pasta Installers para C:\\osc\n"
                "Ou para uma pasta 'osc' dentro deste projeto."
            )
            return

        # Caminhos Relativos
        # __file__ = .../python/dashboard.py
        # root = .../
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        session_file = os.path.join(root_dir, "AbletonLiveOSC", "liveOSC_v2.4.3.json")
        module_file = os.path.join(root_dir, "AbletonLiveOSC", "live_module.js")
        css_file = os.path.join(root_dir, "AbletonLiveOSC", "live.css")
        
        # Configurar Argumentos
        args = [
            osc_exe,
            "--send", "127.0.0.1:11000",
            "--port", "8080",
            "--osc-port", "11001",
            "--load", session_file,
            "--custom-module", module_file,
            "--theme", css_file,
            "--no-gui" # Opcional: Se quiser que ele rode "dentro" dessa app não dá, é Electron.
            # Mas podemos rodar sem bloquear
        ]
        
        try:
            subprocess.Popen(args, cwd=root_dir)
            self.log_manual("Open Stage Control Launched!", "INFO")
        except Exception as e:
            self.log_manual(f"Error launching OSC: {e}", "ERROR")

    def refresh_midi_list(self):
        self.box_out['values'] = mido.get_output_names()
        self.box_in['values'] = mido.get_input_names()

    def apply_midi(self):
        out_port = self.box_out.get()
        in_port = self.box_in.get()
        
        if out_port:
            self.osc_client.send_message("/midi/set_output", out_port)
            self.log_manual(f"Setting MIDI Output to: {out_port}")
            
        if in_port:
            self.osc_client.send_message("/midi/set_input", in_port)
            self.log_manual(f"Setting MIDI Input to: {in_port}")

    def start_server(self):
        # Roda server.py em background
        try:
            # Cria subprocesso sem janela shell, stdout PIPE
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.server_process = subprocess.Popen(
                ["python", "-u", SERVER_SCRIPT], # -u para unbuffered stdout
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redireciona erros para stdout
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Thread para ler stdout
            t = threading.Thread(target=self.reader_thread, daemon=True)
            t.start()
            
            self.log_manual("Background Serve Started...")
            
        except Exception as e:
            self.log_manual(f"Error starting server: {e}", "ERROR")

    def reader_thread(self):
        while True:
            line = self.server_process.stdout.readline()
            if not line:
                break
            self.log_queue.put(line)

    def process_log_queue(self):
        while not self.log_queue.empty():
            line = self.log_queue.get()
            self.append_log(line)
        self.root.after(50, self.process_log_queue)

    def append_log(self, line):
        line = line.strip()
        if not line: return

        # FILTROS
        if "[CLOCK]" in line and not self.show_clock.get(): return
        if "[OSC-JS]" in line and not self.show_osc_js.get(): return
        if "[OSC-IN]" in line and not self.show_osc_in.get(): return
        if "[MIDI" in line and not self.show_midi.get(): return
        if "[TRANSPORT]" in line and not self.show_transport.get(): return
        
        # Tags
        tag = "INFO"
        if "Error" in line or "Exception" in line or "[ERRO" in line:
            tag = "ERROR"
            if not self.show_errors.get(): return
        elif "[OSC-JS]" in line: tag = "OSC-JS"
        elif "[OSC-IN]" in line: tag = "OSC-IN"
        elif "[MIDI" in line: tag = "MIDI"
        elif "[CLOCK]" in line: tag = "DIM"
        
        self.console.configure(state="normal")
        self.console.insert("end", line + "\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def log_manual(self, msg, tag="INFO"):
        self.console.configure(state="normal")
        self.console.insert("end", f">>> {msg}\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
        
    def on_closing(self):
        if self.server_process:
            self.server_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
