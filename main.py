import pygame
import math
import sys
import random
import tkinter as tk
from tkinter import ttk

# =========================================================
# CONFIGURAÇÕES GERAIS E CORES
# =========================================================
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
CINZA_RASTRO = (200, 200, 200)
TEXTO_HUD = (255, 255, 255)

# =========================================================
# CLASSE PISTA 
# =========================================================
class Pista:
    """Responsável por gerar e armazenar os segmentos geométricos da pista"""
    def __init__(self, tipo="quadrado"):
        self.tipo = tipo
        self.segmentos = []
        self.gerar_circuito()

    def gerar_circuito(self):
        if self.tipo == "quadrado":
            p1, p2, p3, p4 = (150, 150), (850, 150), (850, 850), (150, 850)
            self.segmentos = [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]
        elif self.tipo == "hexagono":
            centro_x, centro_y = 500, 500
            raio = 350
            pontos = []
            for i in range(6):
                angulo = i * (2 * math.pi / 6) - math.pi / 6
                x = centro_x + raio * math.cos(angulo)
                y = centro_y + raio * math.sin(angulo)
                pontos.append((x, y))
            for i in range(6):
                self.segmentos.append((pontos[i], pontos[(i + 1) % 6]))

    def verificar_colisao_ponto(self, x, y):
        """Verificação estrita de leitura de pixel (Preto/Branco)"""
        for seg in self.segmentos:
            x1, y1 = seg[0]
            x2, y2 = seg[1]
            px = x2 - x1
            py = y2 - y1
            som_quad = px*px + py*py
            if som_quad == 0: continue
            u = ((x - x1) * px + (y - y1) * py) / float(som_quad)
            u = max(0, min(1, u))
            dx = x1 + u * px - x
            dy = y1 + u * py - y
            if math.hypot(dx, dy) < 3.0: # 3 pixels de espessura da pista
                return True
        return False

# =========================================================
# CLASSE EIXO DO CARRINHO
# =========================================================
class EixoCarrinho:
    """Representa o segmento de 15 pixels e suas extremidades/sensores"""
    def __init__(self, x_ini, y_ini, ang_ini):
        self.comprimento = 15.0
        self.x = x_ini
        self.y = y_ini
        self.angulo = ang_ini
        
        self.esq_x = 0.0
        self.esq_y = 0.0
        self.dir_x = 0.0
        self.dir_y = 0.0
        self.pivo_x = 0.0
        self.pivo_y = 0.0
        self.atualizar_pontos()

    def atualizar_pontos(self):
        metade = self.comprimento / 2.0
        dx = math.cos(self.angulo + math.pi / 2)
        dy = math.sin(self.angulo + math.pi / 2)
        
        self.esq_x = self.x + dx * metade
        self.esq_y = self.y + dy * metade
        self.dir_x = self.x - dx * metade
        self.dir_y = self.y - dy * metade
        
        self.pivo_x = self.x
        self.pivo_y = self.y

    def rotacionar_sobre_ponta_esquerda(self, passo_rad):
        self.angulo += passo_rad
        self.x += math.cos(self.angulo) * 0.2 
        self.y += math.sin(self.angulo) * 0.2
        self.atualizar_pontos()

    def rotacionar_sobre_ponta_direita(self, passo_rad):
        self.angulo -= passo_rad
        self.x += math.cos(self.angulo) * 0.2
        self.y += math.sin(self.angulo) * 0.2
        self.atualizar_pontos()

    def avancar_linear(self, passo_pixel):
        self.x += math.cos(self.angulo) * passo_pixel
        self.y += math.sin(self.angulo) * passo_pixel
        self.atualizar_pontos()

# =========================================================
# CLASSE CARRINHO 
# =========================================================
class Carrinho:
    """Gerencia as decisões de inteligência e regras de negócio do robô"""
    def __init__(self, x_ini, y_ini, ang_ini):
        self.eixo = EixoCarrinho(x_ini, y_ini, ang_ini)
        self.voltas = 0
        self.passou_metade = False
        self.x_start = x_ini
        self.y_start = y_ini
        self.ang_start = ang_ini
        self.ultimo_giro = 0.15

    def ejecutar_passo_logico(self, pista):
        dx_futuro = math.cos(self.eixo.angulo) * 1.0
        dy_futuro = math.sin(self.eixo.angulo) * 1.0
        
        prox_esq_x = self.eixo.esq_x + dx_futuro
        prox_esq_y = self.eixo.esq_y + dy_futuro
        prox_dir_x = self.eixo.dir_x + dx_futuro
        prox_dir_y = self.eixo.dir_y + dy_futuro

        esq_preto = pista.verificar_colisao_ponto(prox_esq_x, prox_esq_y)
        dir_preto = pista.verificar_colisao_ponto(prox_dir_x, prox_dir_y)

        if not esq_preto and not dir_preto:
            self.eixo.avancar_linear(1.0) 
        elif esq_preto and not dir_preto:
            self.eixo.rotacionar_sobre_ponta_esquerda(0.15)
            self.ultimo_giro = 0.15
        elif dir_preto and not esq_preto:
            self.eixo.rotacionar_sobre_ponta_direita(0.15) 
            self.ultimo_giro = -0.15
        else:
            self.eixo.avancar_linear(-0.5)
            self.eixo.angulo += self.ultimo_giro 
            self.eixo.atualizar_pontos()

        dist_start = math.hypot(self.eixo.x - self.x_start, self.eixo.y - self.y_start)
        if dist_start > 250: self.passou_metade = True
        if self.passou_metade and dist_start < 15:
            self.voltas += 1
            self.passou_metade = False

    def resetar(self):
        self.eixo = EixoCarrinho(self.x_start, self.y_start, self.ang_start)
        self.voltas = 0
        self.passou_metade = False
        self.ultimo_giro = 0.15

# =========================================================
# INTERFACE TKINTER 
# =========================================================
class AppTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Carrinho Seguidor de Linha - Modo Tkinter")
        self.root.geometry("1250x1050")
        self.root.resizable(False, False)
        
        self.rodando = False
        self.pista = Pista("quadrado")
        self.carrinho = Carrinho(500.0, 150.0, 0.0)
        self.passos_por_frame = 1 
        
        self.configurar_interface()
        self.desenhar_ambiente_estatico()
        self.atualizar_loop_simulacao()

    def configurar_interface(self):
        self.frame_lateral = ttk.LabelFrame(self.root, text=" Painel de Controle ", padding=15)
        self.frame_lateral.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        
        ttk.Label(self.frame_lateral, text="Selecione o Circuito:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.combo_pista = ttk.Combobox(self.frame_lateral, values=["Quadrado", "Hexágono"], state="readonly")
        self.combo_pista.set("Quadrado")
        self.combo_pista.pack(fill=tk.X, pady=5)
        self.combo_pista.bind("<<ComboboxSelected>>", self.trocar_pista)
        
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill=tk.X, pady=15)
        
        self.btn_play = ttk.Button(self.frame_lateral, text="Iniciar Simulação", command=self.alternar_motores)
        self.btn_play.pack(fill=tk.X, pady=5)
        ttk.Button(self.frame_lateral, text="Resetar Posição", command=self.resetar_tudo).pack(fill=tk.X, pady=5)
        
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill=tk.X, pady=15)
        
        ttk.Label(self.frame_lateral, text="Velocidade da Simulação:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.slider_vel = ttk.Scale(self.frame_lateral, from_=1, to=4, value=1, command=self.ajustar_velocidade)
        self.slider_vel.pack(fill=tk.X, pady=5)
        self.lbl_vel_num = ttk.Label(self.frame_lateral, text="Velocidade: 1x")
        self.lbl_vel_num.pack(anchor=tk.W)
        
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill=tk.X, pady=15)
        
        self.lbl_voltas = ttk.Label(self.frame_lateral, text="Voltas Completas: 0", font=("Arial", 11, "bold"))
        self.lbl_voltas.pack(anchor=tk.W, pady=2)
        self.lbl_pos = ttk.Label(self.frame_lateral, text="X: 0.0 | Y: 0.0", font=("Courier", 10))
        self.lbl_pos.pack(anchor=tk.W, pady=2)
        
        self.canvas_pista = tk.Canvas(self.root, width=1000, height=1000, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas_pista.pack(side=tk.RIGHT, padx=15, pady=15)

    def ajustar_velocidade(self, val):
        self.passos_por_frame = int(float(val))
        self.lbl_vel_num.config(text=f"Velocidade: {self.passos_por_frame}x")

    def alternar_motores(self):
        self.rodando = not self.rodando
        self.btn_play.config(text="Pausar Simulação" if self.rodando else "Iniciar Simulação")

    def trocar_pista(self, event):
        escolha = self.combo_pista.get()
        if choice := escolha:
            if choice == "Quadrado":
                self.pista = Pista("quadrado")
                self.carrinho = Carrinho(500.0, 150.0, 0.0)
            elif choice == "Hexágono":
                self.pista = Pista("hexagono")
                self.carrinho = Carrinho(803.1, 500.0, math.pi / 2)
        self.resetar_tudo()

    def resetar_tudo(self):
        self.carrinho.resetar()
        self.lbl_voltas.config(text="Voltas Completas: 0")
        self.canvas_pista.delete("rastro")
        self.desenhar_ambiente_estatico()

    def desenhar_ambiente_estatico(self):
        self.canvas_pista.delete("pista")
        for seg in self.pista.segmentos:
            self.canvas_pista.create_line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], fill="black", width=3, tags="pista")

    def atualizar_loop_simulacao(self):
        if self.rodando:
            for _ in range(self.passos_por_frame):
                p_ant_x, p_ant_y = self.carrinho.eixo.x, self.carrinho.eixo.y
                self.carrinho.ejecutar_passo_logico(self.pista)
                self.canvas_pista.create_line(p_ant_x, p_ant_y, self.carrinho.eixo.x, self.carrinho.eixo.y, fill="#d8d8d8", width=2, tags="rastro")
            
            self.lbl_voltas.config(text=f"Voltas Completas: {self.carrinho.voltas}")
            self.lbl_pos.config(text=f"X: {self.carrinho.eixo.x:.1f} | Y: {self.carrinho.eixo.y:.1f}")

        pivo_na_pista = self.pista.verificar_colisao_ponto(self.carrinho.eixo.pivo_x, self.carrinho.eixo.pivo_y)
        cor_pivo = "red" if pivo_na_pista else "black"

        self.canvas_pista.delete("carrinho")
        self.canvas_pista.create_line(self.carrinho.eixo.esq_x, self.carrinho.eixo.esq_y, self.carrinho.eixo.dir_x, self.carrinho.eixo.dir_y, fill="black", width=2, tags="carrinho")
        self.canvas_pista.create_oval(self.carrinho.eixo.pivo_x-3, self.carrinho.eixo.pivo_y-3, self.carrinho.eixo.pivo_x+3, self.carrinho.eixo.pivo_y+3, fill=cor_pivo, outline=cor_pivo, tags="carrinho")
        self.canvas_pista.create_oval(self.carrinho.eixo.esq_x-2, self.carrinho.eixo.esq_y-2, self.carrinho.eixo.esq_x+2, self.carrinho.eixo.esq_y+2, fill="#00ff00", tags="carrinho")
        self.canvas_pista.create_oval(self.carrinho.eixo.dir_x-2, self.carrinho.eixo.dir_y-2, self.carrinho.eixo.dir_x+2, self.carrinho.eixo.dir_y+2, fill="#00ff00", tags="carrinho")

        self.root.after(16, self.atualizar_loop_simulacao)


# =========================================================
# INTERFACE PYGAME
# =========================================================
class AmbientePygame:
    def __init__(self):
        self.largura = 1000
        self.altura = 1000
        self.tela = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption("Carrinho Seguidor de Linha - Simulador Pygame")
        self.clock = pygame.time.Clock()
        
        self.canvas = pygame.Surface((self.largura, self.altura))
        self.canvas.fill(BRANCO)
        self.superficie_rastro = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        
        self.fonte = pygame.font.SysFont("consolas", 14)
        self.fonte_menu = pygame.font.SysFont("consolas", 20, bold=True)
        self.fonte_titulo = pygame.font.SysFont("consolas", 36, bold=True)
        self.tempo_inicial = 0
        self.passos_por_frame = 1
        
        self.botoes = {
            "quadrado": pygame.Rect(350, 420, 300, 50),
            "hexagono": pygame.Rect(350, 510, 300, 50),
            "aleatoria": pygame.Rect(350, 600, 300, 50)
        }

    def iniciar_temporizador(self):
        self.tempo_inicial = pygame.time.get_ticks()

    def atualizar(self):
        pygame.display.update()
        self.clock.tick(60)

    def desenhar_menu(self):
        self.tela.fill(BRANCO)
        titulo = self.fonte_titulo.render("SEGUIDOR DE LINHA", True, (40, 40, 50))
        subtitulo = self.fonte_menu.render("Selecione uma pista poligonal", True, (40, 120, 255))
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 180))
        self.tela.blit(subtitulo, (self.largura // 2 - subtitulo.get_width() // 2, 240))
        
        mouse_pos = pygame.mouse.get_pos()
        textos_botoes = {
            "quadrado": "1. Pista Quadrada",
            "hexagono": "2. Pista Hexagonal",
            "aleatoria": "3. Pista Aleatória"
        }
        
        for chave, retangulo in self.botoes.items():
            esta_por_cima = retangulo.collidepoint(mouse_pos)
            cor = (255, 40, 40, 240) if esta_por_cima else (255, 80, 80, 200)
            
            botao_surf = pygame.Surface((retangulo.width, retangulo.height), pygame.SRCALPHA)
            pygame.draw.rect(botao_surf, cor, (0, 0, retangulo.width, retangulo.height), border_radius=8)
            self.tela.blit(botao_surf, (retangulo.x, retangulo.y))
            
            txt_render = self.fonte_menu.render(textos_botoes[chave], True, BRANCO)
            self.tela.blit(txt_render, (retangulo.x + (retangulo.width // 2) - (txt_render.get_width() // 2), retangulo.y + (retangulo.height // 2) - (txt_render.get_height() // 2)))

    def checar_clique_menu(self, mouse_pos):
        for chave, retangulo in self.botoes.items():
            if retangulo.collidepoint(mouse_pos):
                return chave
        return None

    def desenhar_tudo(self, pista, carrinho):
        self.canvas.fill(BRANCO)
        for seg in pista.segmentos:
            pygame.draw.line(self.canvas, PRETO, seg[0], seg[1], 3)
            
        self.tela.blit(self.canvas, (0, 0))
        self.tela.blit(self.superficie_rastro, (0, 0))
        
        p_esq = (int(round(carrinho.eixo.esq_x)), int(round(carrinho.eixo.esq_y)))
        p_dir = (int(round(carrinho.eixo.dir_x)), int(round(carrinho.eixo.dir_y)))
        p_pivo = (int(round(carrinho.eixo.pivo_x)), int(round(carrinho.eixo.pivo_y)))
        
        pivo_na_pista = pista.verificar_colisao_ponto(carrinho.eixo.pivo_x, carrinho.eixo.pivo_y)
        cor_pivo = VERMELHO if pivo_na_pista else PRETO
        
        pygame.draw.line(self.tela, PRETO, p_esq, p_dir, 2)
        pygame.draw.circle(self.tela, cor_pivo, p_pivo, 3) 
        pygame.draw.circle(self.tela, VERDE, p_esq, 2)
        pygame.draw.circle(self.tela, VERDE, p_dir, 2)
        
        self.desenhar_hud(carrinho)

    def desenhar_hud(self, carrinho):
        tempo_seg = (pygame.time.get_ticks() - self.tempo_inicial) / 1000
        infos_telemetria = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Tempo: {tempo_seg:.1f}s",
            f"Voltas: {carrinho.voltas}",
            f"Velocidade: {self.passos_por_frame}x"
        ]
        
        painel_bg = pygame.Surface((160, 100), pygame.SRCALPHA)
        painel_bg.fill((0, 0, 0, 160)) 
        self.tela.blit(painel_bg, (5, 5)) 
        
        y_telemetria = 12
        for info in infos_telemetria:
            render = self.fonte.render(info, True, TEXTO_HUD)
            self.tela.blit(render, (12, y_telemetria))
            y_telemetria += 20

        texto_controles = "Controles: [SETA CIMA] Aumenta Velocidade | [SETA BAIXO] Reduz | [ESC] Menu"
        controles_bg = pygame.Surface((650, 32), pygame.SRCALPHA)
        controles_bg.fill((0, 0, 0, 160)) 
        self.tela.blit(controles_bg, (175, 950))
        render_controles = self.fonte.render(texto_controles, True, TEXTO_HUD)
        self.tela.blit(render_controles, (187, 958))


def iniciar_fluxo_pygame():
    pygame.font.init() 
    ambiente = AmbientePygame()
    estado_jogo = "MENU"
    pista = None
    carrinho = None
    rodando = True

    while rodando:
        if estado_jogo == "MENU":
            ambiente.desenhar_menu()
            ambiente.atualizar()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: rodando = False
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    escolha = ambiente.checar_clique_menu(evento.pos)
                    if escolha is not None:
                        if escolha == "aleatoria":
                            escolha = random.choice(["quadrado", "hexagono"])
                        
                        if escolha == "quadrado":
                            pista = Pista("quadrado")
                            carrinho = Carrinho(500.0, 150.0, 0.0)
                        elif escolha == "hexagono":
                            pista = Pista("hexagono")
                            carrinho = Carrinho(803.1, 500.0, math.pi / 2)
                        
                        ambiente.superficie_rastro.fill((0, 0, 0, 0))
                        ambiente.iniciar_temporizador()
                        estado_jogo = "JOGO"

        elif estado_jogo == "JOGO":
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: rodando = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        ambiente.passos_por_frame = min(ambiente.passos_por_frame + 1, 4)
                    elif evento.key == pygame.K_DOWN:
                        ambiente.passos_por_frame = max(ambiente.passos_por_frame - 1, 1)
                    elif evento.key == pygame.K_ESCAPE:
                        estado_jogo = "MENU"

            for _ in range(ambiente.passos_por_frame):
                p_ant = (int(round(carrinho.eixo.x)), int(round(carrinho.eixo.y)))
                carrinho.ejecutar_passo_logico(pista)
                p_atual = (int(round(carrinho.eixo.x)), int(round(carrinho.eixo.y)))
                pygame.draw.line(ambiente.superficie_rastro, CINZA_RASTRO, p_ant, p_atual, 2)

            if (carrinho.eixo.x < 0 or carrinho.eixo.x > ambiente.largura or
                carrinho.eixo.y < 0 or carrinho.eixo.y > ambiente.altura):
                carrinho.resetar()
                ambiente.superficie_rastro.fill((0, 0, 0, 0))

            ambiente.desenhar_tudo(pista, carrinho)
            ambiente.atualizar()

    pygame.quit()
    sys.exit()


def abrir_seletor_inicial():
    janela_escolha = tk.Tk()
    janela_escolha.title("Seletor de Framework Gráfico")
    janela_escolha.geometry("450x180")  # Reduzido levemente o tamanho vertical já que não há a nota
    janela_escolha.resizable(False, False)
    
    lbl_pergunta = ttk.Label(janela_escolha, text="Qual interface gráfica deseja utilizar para a simulação?", font=("Arial", 11, "bold"), justify=tk.CENTER)
    lbl_pergunta.pack(pady=25)
    
    escolha = {"framework": None}
    
    def selecionar_pygame():
        escolha["framework"] = "pygame"
        janela_escolha.destroy()

    def selecionar_tkinter():
        escolha["framework"] = "tkinter"
        janela_escolha.destroy()
        
    btn_frame = ttk.Frame(janela_escolha)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Abrir em Tkinter", width=20, command=selecionar_tkinter).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Abrir em Pygame", width=20, command=selecionar_pygame).pack(side=tk.LEFT, padx=10)
    
    janela_escolha.mainloop()
    return escolha["framework"]


if __name__ == "__main__":
    pygame.init() 
    framework_escolhido = abrir_seletor_inicial()
    
    if framework_escolhido == "pygame":
        iniciar_fluxo_pygame()
    elif framework_escolhido == "tkinter":
        root_principal = tk.Tk()
        app = AppTkinter(root_principal)
        root_principal.mainloop()