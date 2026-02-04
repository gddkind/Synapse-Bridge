# Synapse Bridge
> **The nervous system for your Live set.**

A high-performance bidirectional control platform for Ableton Live. Using a Python backend as a "nervous bridge," the system connects the DAW to touch interfaces via OSC protocol, enabling real-time visual feedback, low-latency wireless control, and generative functionality expansion.

---

Welcome to Synapse Bridge! Follow the steps below to set up your networked controller.

## 1. Install Python

If you don't have Python installed yet:
1. Download the latest version at [python.org](https://www.python.org/downloads/).
2. **IMPORTANT**: During installation, check the option **"Add Python to PATH"**.

## 2. Install Project Dependencies

1. In this folder, double-click on the file **`INSTALAR_DEPENDENCIAS.bat`**.
2. Wait for the process to finish and show the success message.

## 3. Configure Open Stage Control

This project uses Open Stage Control as the graphical interface.

1. **Download**: Go to the [official download page](https://openstagecontrol.ammd.net/download/) and download the Windows version (`win32-x64`).
2. **Install/Extract**:
   - Extract the contents to a folder of your choice. We recommend: **`C:\osc`**.
   - The final path to the executable should be something like: `C:\osc\open-stage-control.exe`.

   *Tip: If you place it elsewhere, the script will try to search for it, but `C:\osc` is guaranteed to work.*

## 4. Configure Ableton Live (Remote Script)

Ableton needs a special script to "talk" to our system.

1. Copy the `AbletonOSC` folder found inside `Ableton_Remote_Script` in this package.
2. Paste this folder into your Ableton Live's "MIDI Remote Scripts" directory.
   - **Windows (Default)**: `C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Scripts\`
   - *Note: ProgramData is a hidden folder. You can type `%ProgramData%` in the Windows Explorer address bar.*

3. Open Ableton Live.
4. Go to **Options -> Preferences -> Link/Tempo/MIDI**.
5. In the **Control Surface** section, look for **AbletonOSC** in the list and select it.
6. The Input/Output ports can be set to "None" or matched to your specific MIDI setup (LoopMIDI), but simply selecting the script activates the network port.

## 5. Run the Project!

1. Make sure **Open Stage Control** is in the correct folder or that you know where it is.
2. With Ableton open, double-click on **`INICIAR_PROJETO.bat`**.
3. The Dashboard will open.
4. In the Dashboard, click **LAUNCH INTERFACE**.
   - *If you get a "not found" error, verify if `open-stage-control.exe` is in `C:\osc` or in the `osc` folder within the project.*
5. Scan the QR Code with your phone/tablet.
6. Have fun!

## Troubleshooting

- **Firewall**: If your phone doesn't connect, allow Python and ports 8080/8090 in your Firewall settings.
- **Open Stage Control won't open**: Double-check if you downloaded and extracted the program correctly in the steps above.

---
## Credits & Tools

This project was built by integrating amazing open-source technologies. For full functionality, you will also need a Virtual MIDI driver:

### Required Software (Target System)
- **[loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)**: To create virtual MIDI ports.
- **[Open Stage Control](https://openstagecontrol.ammd.net/download/)**: The graphical interface (Download Required).

### Open Source Projects Used (Credits)
**Note:** The integration codes and layouts are already included. Only the external software mentioned above needs to be installed.

1. **[AbletonOSC (Remote Script)](https://github.com/ideoforms/AbletonOSC)**
   - *By Daniel Jones (ideoforms)*
   - Included in the `Ableton_Remote_Script` folder.
   - The heart of the OSC integration.

2. **[Open Stage Control](https://framagit.org/jean-emmanuel/open-stage-control)**
   - *By Jean-Emmanuel*
   - Interface software (Separate download required).

3. **[AbletonLiveOSC (Layout)](https://github.com/ziginfo/OpenStageControl-Layouts/tree/main/AbletonLiveOSC)**
   - *By ziginfo*
   - Included in the `AbletonLiveOSC` folder.
   - The visual design and slider/button logic.

---
## Authorship & Vibe Coding

This project was built on the foundation of **Vibe Coding**, uniting human creativity and artificial intelligence.

- **Guilherme Dedekind**: Concept, Assembly, and Curation.
- **Various Random AIs**: Script generation, Debugging, and Moral Support.

---
Powered by AbletonOSC Bridge technology.
