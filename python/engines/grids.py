import math
import random
import threading

class GridsEngine:
    def __init__(self, osc_client):
        self.client = osc_client
        self.lock = threading.Lock()
        
        self.step = 0
        self.resolution = 32
        self.is_playing = False # Play/Stop state
        
        # Parâmetros controláveis (0.0 a 1.0)
        self.map_x = 0.5
        self.map_y = 0.5
        self.chaos = 0.0
        
        # Densidade de cada instrumento (BD, SD, HH)
        self.density = [0.5, 0.5, 0.5] 
        
        # Estado interno 
        self.perturbations = [0.0] * 3

    def update_param(self, name, value):
        with self.lock:
            # Garante float
            val = float(value)
            if name == 'map_x': self.map_x = val
            elif name == 'map_y': self.map_y = val
            elif name == 'chaos': self.chaos = val
            elif name.startswith('density'):
                # Esperado: density_0, density_1...
                parts = name.split('_')
                if len(parts) > 1:
                    idx = int(parts[1])
                    if 0 <= idx < 3:
                        self.density[idx] = val

    def _get_base_density(self, instrument, step, x, y):
        # Lógica Matemática Original do Mutable Instruments Grids
        # Portada do seu script grids_replica.py
        
        val = 0.0
        
        if instrument == 0: # KICK (BD)
            is_downbeat = (step % 4 == 0)
            pat_a = 1.0 if is_downbeat else 0.1
            pat_b = 1.0 if (step % 8 == 0 or step % 8 == 5 or step % 8 == 2) else 0.0
            base = pat_a * (1 - x) + pat_b * x
            if y > 0.5:
                if step % 2 == 0: base += (y - 0.5) * 0.5
            val = base

        elif instrument == 1: # SNARE (SD)
            is_backbeat = (step % 8 == 4) 
            pat_a = 1.0 if is_backbeat else 0.0
            pat_b = 1.0 if is_backbeat else (0.4 if step % 2 == 0 else 0.0)
            base = pat_a * (1 - y) + pat_b * y
            if x > 0.7:
                if step % 8 == 7: base += (x - 0.7)
            val = base

        elif instrument == 2: # HI-HAT (HH)
            base = 0.5 
            if step % 4 == 0: base += 0.3
            elif step % 2 == 0: base += 0.1
            if x < 0.3: 
                if step % 4 != 2: base -= 0.3
            if y > 0.6:
                if step % 2 != 0: base += (y-0.6)
            val = base

        return min(max(val, 0.0), 1.0)

    def process_step(self):
        """Calcula o próximo passo do sequenciador e retorna triggers"""
        if not self.is_playing:
            return []
            
        triggers = []
        with self.lock:
            # 1. Aplica Caos (Perturbações aleatórias nas densidades)
            if self.chaos > 0 and random.random() < 0.1:
                for i in range(3):
                    self.perturbations[i] = (random.random() - 0.5) * self.chaos * 2.0
            
            # 2. Avalia cada instrumento
            for i in range(3):
                # Obtem densidade base do mapa (coordenadas X/Y)
                map_val = self._get_base_density(i, self.step, self.map_x, self.map_y)
                
                # Soma perturbação de caos
                if self.chaos > 0:
                    map_val += self.perturbations[i]
                
                # Soma offset de densidade do usuário ("Fill")
                # (density - 0.5) permite aumentar ou diminuir a probabilidade
                combined_val = map_val + (self.density[i] - 0.5)
                
                # Limiar de disparo. 
                # (Se o valor calculado for maior que 0.4, toca nota)
                threshold = 0.4
                
                if combined_val > threshold:
                    # Calcula velocity baseado em quão forte passou do limiar
                    vel_float = min(1.0, (combined_val - threshold) * 2.0)
                    velocity = int(60 + vel_float * 67) # Velocity entre 60 e 127
                    triggers.append((i, velocity))
            
            # Avança o passo (loop de 32 passos = 2 compassos)
            self.step = (self.step + 1) % self.resolution
            
        return triggers
