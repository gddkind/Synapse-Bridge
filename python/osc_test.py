from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import argparse
import time
import threading

# Configurações Padrão do AbletonOSC
# Ableton escuta na 11000 (nós enviamos para cá)
# Ableton envia para 11001 (nós escutamos aqui)
ABLETON_IP = "127.0.0.1"
ABLETON_PORT = 11000
LISTEN_PORT = 11001

def print_handler(address, *args):
    print(f"[RECV] {address}: {args}")

def run_server(ip, port):
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(print_handler)
    
    server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
    print(f"[*] Servidor OSC ouvindo em {ip}:{port}")
    server.serve_forever()

def main():
    print("=== AbletonOSC Tester ===")
    print(f"Alvo: {ABLETON_IP}:{ABLETON_PORT}")
    print(f"Escuta: localhost:{LISTEN_PORT}")
    print("=========================")

    # Iniciar servidor em uma thread separada
    server_thread = threading.Thread(target=run_server, args=("127.0.0.1", LISTEN_PORT))
    server_thread.daemon = True
    server_thread.start()

    client = udp_client.SimpleUDPClient(ABLETON_IP, ABLETON_PORT)

    time.sleep(1) # Aguarda servidor subir

    try:
        while True:
            print("\nComandos disponíveis:")
            print("1. Teste de Conexão (/live/test)")
            print("2. Tocar (/live/song/start_playing)")
            print("3. Parar (/live/song/stop_playing)")
            print("4. Status Atual (/live/song/get/current_song_time)")
            print("q. Sair")
            
            cmd = input("Escolha: ").strip().lower()
            
            if cmd == '1':
                print("[SEND] /live/test")
                client.send_message("/live/test", [])
            elif cmd == '2':
                print("[SEND] /live/song/start_playing")
                client.send_message("/live/song/start_playing", [])
            elif cmd == '3':
                print("[SEND] /live/song/stop_playing")
                client.send_message("/live/song/stop_playing", [])
            elif cmd == '4':
                print("[SEND] /live/song/get/current_song_time")
                client.send_message("/live/song/get/current_song_time", [])
            elif cmd == 'q':
                break
            else:
                print("Comando inválido.")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nSaindo...")

if __name__ == "__main__":
    main()
