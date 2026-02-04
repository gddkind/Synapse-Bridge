from aiohttp import web
import socketio
import asyncio
from pythonosc import udp_client
from config import *
import threading
import time

# Setup OSC
osc_client = udp_client.SimpleUDPClient(ABLETON_IP, ABLETON_OSC_PORT)

# Setup Socket.IO (Async)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Servir arquivos estáticos (PWA)
async def index(request):
    return web.FileResponse('pwa/index.html')

app.router.add_get('/', index)

# Engine Mock
import engines.grids
grids = engines.grids.GridsEngine(osc_client)



@sio.event
async def control(sid, data):
    # data = {'param': 'map_x', 'value': 0.5}
    # print(f"Control: {data}")
    
    if data['param'] in ['map_x', 'map_y', 'chaos', 'density_0', 'density_1', 'density_2']:
        grids.update_param(data['param'], data['value'])
        
        # Log genérico para todos os parâmetros
        print(f"[GRIDS] {data['param']}: {float(data['value']):.2f}")
        
        # EXPERIMENTAL: Mapear Chaos para o Send A da Track 1 no Ableton
        # Só pra mostrar a força do OSC
        if data['param'] == 'chaos':
            # /live/track/set/send track_index send_index value
            osc_client.send_message("/live/track/set/send", [0, 0, float(data['value'])])

# Helper: Encontrar porta LoopMIDI
import mido

# MIDI Globals
midi_out = None
midi_in = None
midi_port_name_out = "None"
midi_port_name_in = "None"

import tkinter as tk
from tkinter import ttk

def midi_input_handler(msg):
    """Recebe MIDI do Ableton e manda para o OSC (Feedback de Luzes)"""
    # Ex: Note ON 36 (Kick) -> OSC /note/36 1
    # OSC geralmente espera address tipo /midi/note ou custom
    # Vamos mandar um formato genérico que o JS possa parsear ou Address direto se configurado
    
    if msg.type == 'note_on' and msg.velocity > 0:
        # Envia para o OSC na porta 1337 (Server) -> JS (Client)?
        # Não, feedback de luz tem que ir para o Client do Open Stage Control
        # Porta 9000 (osc_gui_client)
        osc_gui_client.send_message(f"/feedback/note/{msg.note}", 1.0)
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        osc_gui_client.send_message(f"/feedback/note/{msg.note}", 0.0)

def auto_connect_midi():
    global midi_out, midi_in, midi_port_name_out, midi_port_name_in
    
    outputs = mido.get_output_names()
    inputs = mido.get_input_names()
    
    if not outputs:
        print("[MIDI] Nenhuma porta encontrada.")
        return

    # Janela de Seleção Dupla
    root = tk.Tk()
    root.title("Conexão MIDI Dupla (AbletonOSC)")
    root.geometry("450x250")
    
    # OUTPUT (Send to Live)
    lbl_out = tk.Label(root, text="SAÍDA (Envia notas para o Ableton):", font=("bold"))
    lbl_out.pack(pady=(10, 0))
    combo_out = ttk.Combobox(root, values=outputs, width=50)
    if outputs: combo_out.current(0)
    combo_out.pack()
    
    # INPUT (Feedback from Live)
    lbl_in = tk.Label(root, text="ENTRADA (Recebe feedback do Ableton - Luzes):", font=("bold"))
    lbl_in.pack(pady=(15, 0))
    combo_in = ttk.Combobox(root, values=inputs, width=50)
    if inputs: combo_in.current(0)
    combo_in.pack()
    
    sel_out = [None]
    sel_in = [None]
    
    def on_connect():
        sel_out[0] = combo_out.get()
        sel_in[0] = combo_in.get()
        root.destroy()
        
    btn = tk.Button(root, text="Conectar MIDI", command=on_connect, bg="#4CAF50", fg="white", height=2)
    btn.pack(pady=20, fill="x", padx=20)
    
    root.eval('tk::PlaceWindow . center')
    root.focus_force()
    root.mainloop()
    
    # Conectar OUTPUT
    target_out = sel_out[0]
    if target_out:
        try:
            if midi_out: midi_out.close()
            midi_out = mido.open_output(target_out)
            midi_port_name_out = target_out
            print(f"[MIDI OUT] Conectado: {target_out}")
        except Exception as e:
            print(f"[ERRO MIDI OUT] {e}")

    # Conectar INPUT (Feedback)
    target_in = sel_in[0]
    if target_in:
        try:
            if midi_in: midi_in.close()
            # Callback=None por enquanto, vamos poll ou thread depois?
            # Mido input com callback é o ideal
            midi_in = mido.open_input(target_in, callback=midi_input_handler)
            midi_port_name_in = target_in
            print(f"[MIDI IN]  Conectado: {target_in} (Feedback Ativo)")
        except Exception as e:
            print(f"[ERRO MIDI IN] {e}")

# Conecta no inicio com GUI
# auto_connect_midi()

@sio.event
async def connect(sid, environ):
    print(f"Web Client Connected: {sid}")
    await sio.emit('status', {'msg': 'Connected to Python Bridge'})
    ports_out = mido.get_output_names()
    ports_in = mido.get_input_names()
    await sio.emit('midi_ports', {'outs': ports_out, 'ins': ports_in})
    
    # ... resto do sync ...

    state = {
        'is_playing': grids.is_playing,
        'map_x': grids.map_x,
        'map_y': grids.map_y,
        'chaos': grids.chaos,
        'density_0': grids.density[0],
        'density_1': grids.density[1],
        'density_2': grids.density[2]
    }
    await sio.emit('state_sync', state)

@sio.event
async def toggle_play(sid, data):
    grids.is_playing = not grids.is_playing
    print(f"[TRANSPORT] Playing: {grids.is_playing}")
    
    # Avisa todos os clientes (para atualizar o botão se tiver mais de um aberto)
    await sio.emit('play_state', {'is_playing': grids.is_playing})
    
    # Opcional: Dar play no Ableton também?
    # osc_client.send_message("/live/song/start_playing" if grids.is_playing else "/live/song/stop_playing", [])

@sio.event
async def set_midi_port(sid, data):
    global midi_out, midi_port_name
    port_name = data.get('port')
    print(f"[MIDI] Trocando para: {port_name}")
    
    if midi_out:
        midi_out.close()
        midi_out = None
        
    try:
        midi_out = mido.open_output(port_name)
        midi_port_name = port_name
        await sio.emit('status', {'msg': f'MIDI Output: {port_name}'})
    except Exception as e:
        print(f"Erro ao trocar porta: {e}")

# ... imports existentes ...
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

# Setup O-S-C Client (Envia para o GUI na 9000)
osc_gui_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

# Handlers OSC (Recebe do GUI na 1337)
def osc_handler_param(address, *args):
    # address: /grids/map_x -> param: map_x
    param = address.split('/')[-1]
    value = args[0]
    
    # Atualiza Engine
    grids.update_param(param, value)
    
    # Log
    print(f"[OSC-IN] {param}: {value:.2f}")
    
    # Feedback para SIO (PWA) e O-S-C (GUI)
    # (O-S-C geralmente atualiza sozinho se address bater, mas é bom syncar)
    # osc_gui_client.send_message(address, value) 

def osc_handler_play(address, *args):
    value = args[0]
    grids.is_playing = bool(value)
    print(f"[TRANSPORT] Play: {grids.is_playing}")
    
    # Sync PWA
    asyncio.create_task(sio.emit('play_state', {'is_playing': grids.is_playing}))

def osc_handler_reset(address, *args):
    print("[OSC] Resetting Grids Defaults")
    grids.map_x = 0.5
    grids.map_y = 0.5
    grids.chaos = 0.0
    # Envia de volta pro GUI atualizar sliders
    osc_gui_client.send_message("/grids/map_x", 0.5)
    osc_gui_client.send_message("/grids/map_y", 0.5)
    osc_gui_client.send_message("/grids/chaos", 0.0)

def osc_handler_note(address, *args):
    """
    Recebe: /note channel note velocity
    Envia MIDI para a porta configurada.
    """
    if not midi_out:
        return

    try:
        # args geralmente vem como float do OSC, converter para int
        channel = int(args[0]) - 1 # MIDI é 0-15, mas OSC pode mandar 1-16
        if channel < 0: channel = 0
        
        note = int(args[1])
        velocity = int(args[2])
        
        # print(f"[MIDI-BRIDGE] Ch:{channel+1} Note:{note} Vel:{velocity}")
        
        if velocity > 0:
            msg = mido.Message('note_on', channel=channel, note=note, velocity=velocity)
        else:
            msg = mido.Message('note_off', channel=channel, note=note, velocity=0)
            
        midi_out.send(msg)
        
    except Exception as e:
        print(f"[ERRO MIDI] {e}")

# Dispatcher Config
dispatcher = Dispatcher()
dispatcher.map("/grids/map_x", osc_handler_param)
dispatcher.map("/grids/map_y", osc_handler_param)
dispatcher.map("/grids/chaos", osc_handler_param)
dispatcher.map("/grids/play", osc_handler_play)
dispatcher.map("/grids/reset", osc_handler_reset)
dispatcher.map("/note", osc_handler_note)

def osc_handler_set_midi_out(address, *args):
    """Define porta MIDI Out via OSC"""
    global midi_out, midi_port_name_out
    port_name = args[0]
    print(f"[MIDI-CONFIG] Request Output: {port_name}")
    try:
        if midi_out: midi_out.close()
        midi_out = mido.open_output(port_name)
        midi_port_name_out = port_name
        print(f"[MIDI OUT] Conectado: {port_name}")
    except Exception as e:
        print(f"[ERRO MIDI OUT] {e}")

def osc_handler_set_midi_in(address, *args):
    """Define porta MIDI In via OSC"""
    global midi_in, midi_port_name_in
    port_name = args[0]
    print(f"[MIDI-CONFIG] Request Input: {port_name}")
    try:
        if midi_in: midi_in.close()
        midi_in = mido.open_input(port_name, callback=midi_input_handler)
        midi_port_name_in = port_name
        print(f"[MIDI IN] Conectado: {port_name}")
    except Exception as e:
        print(f"[ERRO MIDI IN] {e}")

dispatcher.map("/midi/set_output", osc_handler_set_midi_out)
dispatcher.map("/midi/set_input", osc_handler_set_midi_in)

# Conecta no inicio com GUI (DESATIVADO PARA DASHBOARD)
# auto_connect_midi()

def osc_handler_log(address, *args):
    """Captura logs vindos do Open Stage Control (JS)"""
    msg = args[0]
    print(f"[OSC-JS] {msg}")

dispatcher.map("/log", osc_handler_log)

def log_to_gui(msg):
    """Envia log do Python para o Console do Open Stage Control"""
    print(f"[PY-LOG] {msg}")
    osc_gui_client.send_message("/LOG", f"[PY] {msg}")

# ... resto do código ...

async def background_loop():
    """Simula o clock interno"""
    print("[CLOCK] Loop ativo.")
    while True:
        triggers = grids.process_step()
        if triggers:
            for inst, vel in triggers:
                note = MIDI_NOTE_KICK if inst == 0 else (MIDI_NOTE_SNARE if inst == 1 else MIDI_NOTE_HH_CLOSED)
                
                # Feedback para GUI (Visualizer)
                # O-S-C não tem visualizer nativo rápido igual JS, mas podemos mandar msg
                # osc_gui_client.send_message(f"/grids/trigger/{inst}", 1.0)
                
                await sio.emit('trigger', {'instrument': inst, 'velocity': vel})
                
                if midi_out:
                    try:
                        midi_out.send(mido.Message('note_on', note=note, velocity=int(vel), channel=9))
                        midi_out.send(mido.Message('note_off', note=note, velocity=0, channel=9))
                    except:
                        pass # Ignora erros de envio se a porta morrer
        
        await asyncio.sleep(60/120/4)

async def main():
    # 1. Start Web Server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', WEB_PORT)
    print(f"=== AbletonOSC Bridge Running on http://localhost:{WEB_PORT} ===")
    
    # 2. Start OSC Server (Async)
    # Escuta na porta 1337 (O-S-C manda pra cá)
    server = AsyncIOOSCUDPServer(("127.0.0.1", 1337), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    print(f"=== OSC Server Listening on 1337 ===")

    # 3. Background Tasks
    asyncio.create_task(background_loop())
    
    await site.start()
    
    # Keep alive
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
