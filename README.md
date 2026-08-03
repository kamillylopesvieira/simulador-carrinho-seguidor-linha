# 🏎️ Simulador de Robô Seguidor de Linha

Um simulador gráfico bidimensional em **Python** que modela o comportamento de um robô móvel seguidor de linha em malha fechada. O sistema simula a leitura de sensores ópticos virtuais e aplica uma lógica de correção angular dinâmica para manter o veículo no trajeto.

---

## 📸 Demonstração

![Demonstração do Simulador](demons-simulador.gif)

---

## 🚀 Funcionalidades

- **Múltiplos Frameworks Gráficos:** Permite escolher entre simulação via **Pygame** ou **Tkinter** no arranque.
- **Circuitos Poligonais:** Suporte para pistas nos formatos **Quadrado** e **Hexagonal**.
- **Lógica de Sensores Virtuais:** Detecta o contraste entre a linha preta (pista) e o fundo branco utilizando sensores posicionados nas extremidades do eixo do carrinho.
- **HUD Completo:** Exibição em tempo real de:
  - Tempo decorrido;
  - Taxa de quadros por segundo (FPS);
  - Contador de voltas por aproximação geométrica;
  - Multiplicador de velocidade.
- **Rastro Persistente:** Desenho do caminho percorrido pelo robô para análise de estabilidade do trajeto.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Pygame**
- **Tkinter**

---

## 📋 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de que tem o Python 3 instalado no seu computador.

### 2. Instalar dependências
No terminal ou prompt de comando, instale a biblioteca Pygame:
```bash
pip install pygame
```
3. Executar o simulador
Inicie o programa executando o ficheiro principal:
```bash
python main.py
```
## ⚙️ Controles e Interação

 Menu Inicial: Escolha a interface gráfica (Pygame/Tkinter) e o circuito desejado por clique.
 Tkinter: apenas mouse 
 Pygame: seta para cima e seta para baixo, descrições na interface.

✨ Projeto desenvolvido para fins de estudo em robótica móvel, lógica de controle e simulação computacional.
