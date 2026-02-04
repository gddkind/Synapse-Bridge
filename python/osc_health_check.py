from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import time
import threading
import sys

# Configurações
ABLETON_IP = "127.0.0.1"
ABLETON_PORT = 11000
LISTEN_PORT = 11001

received = False

def handler(address, *args):
    global received
    print(f"Recebido: {address} {args}")
    received = True

def run_server():
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handler)
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", LISTEN_PORT), disp)
    server.timeout = 0.5
    start = time.time()
    # Roda por 3 segundos
    while time.time() - start < 3:
        server.handle_request()

def main():
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    client = udp_client.SimpleUDPClient(ABLETON_IP, ABLETON_PORT)
    
    print("Enviando ping para o Ableton...")
    # Tenta alguns comandos comuns que devem retornar resposta imediatamente se conectado
    client.send_message("/live/test", [])
    client.send_message("/live/song/get/current_song_time", [])
    
    server_thread.join()
    
    if received:
        print("SUCESSO: Resposta recebida do Ableton!")
        sys.exit(0)
    else:
        print("FALHA: Nenhuma resposta do Ableton em 3 segundos.")
        sys.exit(1)

if __name__ == "__main__":
    main()
