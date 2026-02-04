# Synapse Bridge
> **The nervous system for your Live set.**

Uma plataforma de controle bidirecional de alta performance para Ableton Live. Utilizando um backend em Python como "ponte nervosa", o sistema conecta a DAW a interfaces touch via protocolo OSC, permitindo feedback visual em tempo real, controle sem fio de baixa latência e expansão generativa de funcionalidades.

---

Bem-vindo ao Synapse Bridge! Siga os passos abaixo para configurar seu controlador network.

## 1. Instalar Python

Se você ainda não tem o Python instalado:
1. Baixe a versão mais recente em [python.org](https://www.python.org/downloads/).
2. **IMPORTANTE**: Durante a instalação, marque a opção **"Add Python to PATH"**.

## 2. Instalar Dependências do Projeto

1. Nesta pasta, dê um duplo clique no arquivo **`INSTALAR_DEPENDENCIAS.bat`**.
2. Aguarde o processo finalizar e mostrar a mensagem de sucesso.

## 3. Configurar o Open Stage Control

Este projeto utiliza o Open Stage Control como interface gráfica.

1. **Baixe o programa**: Acesse a [página de download oficial](https://openstagecontrol.ammd.net/download/) e baixe a versão para Windows (`win32-x64`).
2. **Instale/Extraia**:
   - Extraia o conteúdo para uma pasta de sua preferência. Recomendamos: **`C:\osc`**.
   - O caminho final do executável deve ficar algo como: `C:\osc\open-stage-control.exe`.

   *Dica: Se você colocar em outro lugar, o script tentará procurar, mas `C:\osc` é o garantido.*

## 4. Configurar o Ableton Live (Remote Script)

O Ableton precisa de um script especial para "conversar" com nosso sistema.

1. Copie a pasta `AbletonOSC` que está dentro de `Ableton_Remote_Script` neste pacote.
2. Cole essa pasta dentro do diretório de "MIDI Remote Scripts" do seu Ableton Live.
   - **Windows (Padrão)**: `C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Scripts\`
   - *Nota: A pasta ProgramData é oculta. Você pode digitar `%ProgramData%` na barra de endereço do Windows Explorer.*

3. Abra o Ableton Live.
4. Vá em **Options -> Preferences -> Link/Tempo/MIDI**.
5. Na seção **Control Surface**, procure por **AbletonOSC** na lista e selecione-o.
6. As entradas e saídas (Input/Output) podem ficar como "None" ou conforme seu setup MIDI específico (LoopMIDI), mas selecionar o script já ativa a porta de rede.

## 5. Rodar o Projeto!

1. Certifique-se que o **Open Stage Control** está na pasta correta ou que você sabe onde ele está.
2. Com o Ableton aberto, dê duplo clique em **`INICIAR_PROJETO.bat`**.
3. O Dashboard irá abrir.
4. No Dashboard, clique em **LAUNCH INTERFACE**.
   - *Se der erro "não encontrado", verifique se o arquivo `open-stage-control.exe` está em `C:\osc` ou na pasta `osc` dentro do projeto.*
5. Escaneie o QR Code com seu celular/tablet.
6. Divirta-se!

## Solução de Problemas

- **Firewall**: Se o celular não conectar, libere o Python e as portas 8080/8090 no Firewall.
- **Open Stage Control não abre**: Verifique se baixou e extraiu o programa corretamente nos passos acima.

---
## Créditos e Ferramentas

Este projeto foi construído integrando tecnlogias incríveis da comunidade Open Source. Para o funcionamento completo, você precisará também de um driver MIDI Virtual:

### Software Necessário (Externo)
- **[loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)**: Para criar portas MIDI virtuais.
- **[Open Stage Control](https://openstagecontrol.ammd.net/download/)**: A interface gráfica (Download Necessário).

### Projetos Open Source Utilizados (Créditos)
**Nota:** Os códigos de integração e layouts já estão inclusos. Apenas os softwares externos acima precisam ser instalados.

1. **[AbletonOSC (Remote Script)](https://github.com/ideoforms/AbletonOSC)**
   - *Por Daniel Jones (ideoforms)*
   - Incluso na pasta `Ableton_Remote_Script`.
   - O coração da integração via OSC.

2. **[Open Stage Control](https://framagit.org/jean-emmanuel/open-stage-control)**
   - *Por Jean-Emmanuel*
   - Software de interface (Download separado requerido).

3. **[AbletonLiveOSC (Layout)](https://github.com/ziginfo/OpenStageControl-Layouts/tree/main/AbletonLiveOSC)**
   - *Por ziginfo*
   - Incluso na pasta `AbletonLiveOSC`.
   - O design visual e lógica dos faders/botões.

---
## Autoria & Vibe Coding

Este projeto foi construído na base do **Vibe Coding**, unindo criatividade humana e inteligência artificial.

- **Guilherme Dedekind**: Concepção, Montagem e Curadoria.
- **Várias IAs Aleatórias**: Geração de scripts, Debugging e Apoio Moral.

---
Desenvolvido com tecnologia AbletonOSC Bridge.
