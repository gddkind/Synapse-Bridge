import argparse
import random
import time
from pythonosc import udp_client
from pythonosc import osc_server
from pythonosc import dispatcher
import threading

# Config
REMOTE_IP = "127.0.0.1"
REMOTE_PORT = 11000
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 11001

received = False

def handle_response(address, *args):
    global received
    print(f"[SUCESSO] Recebido de Ableton: {address} {args}")
    received = True

def start_server():
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_response)
    server = osc_server.ThreadingOSCUDPServer((LISTEN_IP, LISTEN_PORT), disp)
    print(f"Ouvindo em {LISTEN_PORT}...")
    server.timeout = 0.5
    start = time.time()
    while not received and (time.time() - start < 3):
        server.handle_request()

def main():
    # Start Listener
    t = threading.Thread(target=start_server)
    t.start()

    # Send Ping
    client = udp_client.SimpleUDPClient(REMOTE_IP, REMOTE_PORT)
    print(f"Enviando teste para {REMOTE_PORT}...")
    client.send_message("/live/test", [])
    client.send_message("/live/song/get/current_song_time", [])
    
    t.join()
    
    if received:
        print("\n>>> CONEXÃO ESTABELECIDA COM SUCESSO <<<")
    else:
        print("\n>>> FALHA: SEM RESPOSTA DO ABLETON <<<")
        print("Verifique:")
        print("1. Se o Ableton está aberto.")
        print("2. Se 'AbletonOSC' está selecionado em Control Surface.")
        print("3. Se não há erro no log do Ableton.")

if __name__ == "__main__":
    main()
