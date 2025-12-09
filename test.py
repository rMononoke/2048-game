import pygame
import random
import sys
import os
from config import *


# --- ЛОГИКА ИГРЫ (Без изменений) ---

def load_high_score():
    if not os.path.exists(HIGHSCORE_FILE): return 0
    try:
        with open(HIGHSCORE_FILE, "r") as f: return int(f.read())
    except: return 0

def save_high_score(score):
    with open(HIGHSCORE_FILE, "w") as f: f.write(str(score))

def init_board(size):
    board = [[0] * size for _ in range(size)]
    add_new_tile(board, size)
    add_new_tile(board, size)
    return board

def add_new_tile(board, size):
    empty_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 4 if random.random() > 0.9 else 2

def compress(board, size):
    new_board = [[0] * size for _ in range(size)]
    for r in range(size):
        pos = 0
        for c in range(size):
            if board[r][c] != 0:
                new_board[r][pos] = board[r][c]
                pos += 1
    return new_board

def merge(board, score, size):
    for r in range(size):
        for c in range(size - 1):
            if board[r][c] != 0 and board[r][c] == board[r][c + 1]:
                board[r][c] *= 2
                board[r][c + 1] = 0
                score += board[r][c]
    return board, score

def reverse(board, size):
    new_board = []
    for r in range(size):
        new_board.append([])
        for c in range(size):
            new_board[r].append(board[r][size - 1 - c])
    return new_board

def transpose(board, size):
    new_board = [[0] * size for _ in range(size)]
    for r in range(size):
        for c in range(size):
            new_board[r][c] = board[c][r]
    return new_board

def move_left(board, score, size):
    board = compress(board, size)
    board, score = merge(board, score, size)
    board = compress(board, size)
    return board, score

def move_right(board, score, size):
    board = reverse(board, size)
    board, score = move_left(board, score, size)
    board = reverse(board, size)
    return board, score

def move_up(board, score, size):
    board = transpose(board, size)
    board, score = move_left(board, score, size)
    board = transpose(board, size)
    return board, score

def move_down(board, score, size):
    board = transpose(board, size)
    board, score = move_right(board, score, size)
    board = transpose(board, size)
    return board, score

def check_game_over(board, size):
    for r in range(size):
        for c in range(size):
            if board[r][c] == 0: return False
    for r in range(size):
        for c in range(size - 1):
            if board[r][c] == board[r][c + 1]: return False
            if board[c][r] == board[c + 1][r]: return False
    return True

# --- КЛАСС КНОПКИ ---
class Button:
    def __init__(self, x, y, w, h, text, callback, param=None, selected=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.param = param
        self.selected = selected

    def draw(self, screen, font, theme_colors):
        # Цвет кнопки зависит от того, выбрана она или нет
        color = (100, 200, 100) if self.selected else theme_colors["button"]
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Обводка для красоты
        pygame.draw.rect(screen, theme_colors["button_text"], self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, theme_colors["button_text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.param:
                    self.callback(self.param)
                else:
                    self.callback()
                return True
        return False

# --- ОСНОВНАЯ ПРОГРАММА ---

def run_game(grid_size_choice, theme_choice):
    """Запуск самой игры"""
    global GRID_SIZE, WIDTH, HEIGHT, TILE_SIZE
    GRID_SIZE = grid_size_choice
    
    # Настройки темы
    current_theme = THEMES[theme_choice]
    
    # Пересчет размеров окна
    WIDTH = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GRID_PADDING
    HEIGHT = WIDTH + 100
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"2048 | {grid_size_choice}x{grid_size_choice}")
    clock = pygame.time.Clock()
    
    font_score = pygame.font.SysFont("arial", 24, bold=True)
    font_tile = pygame.font.SysFont("arial", 36, bold=True)
    
    board = init_board(GRID_SIZE)
    score = 0
    high_score = load_high_score()
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(high_score)
                return "QUIT" # Выход из игры полностью
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_high_score(high_score)
                    return "MENU" # Возврат в меню

                if not game_over:
                    old_board = [row[:] for row in board]
                    
                    if event.key == pygame.K_LEFT:
                        board, score = move_left(board, score, GRID_SIZE)
                    elif event.key == pygame.K_RIGHT:
                        board, score = move_right(board, score, GRID_SIZE)
                    elif event.key == pygame.K_UP:
                        board, score = move_up(board, score, GRID_SIZE)
                    elif event.key == pygame.K_DOWN:
                        board, score = move_down(board, score, GRID_SIZE)
                    elif event.key == pygame.K_r:
                        board = init_board(GRID_SIZE)
                        score = 0
                    
                    if old_board != board:
                        add_new_tile(board, GRID_SIZE)
                        if score > high_score: high_score = score
                        if check_game_over(board, GRID_SIZE):
                            game_over = True
                            save_high_score(high_score)

        # Отрисовка
        screen.fill(current_theme["bg"])
        
        # Счет
        score_text = font_score.render(f"Score: {score}", True, current_theme["text"])
        high_text = font_score.render(f"Best: {high_score}", True, current_theme["text"])
        screen.blit(score_text, (20, 20))
        high_rect = high_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(high_text, high_rect)

        # Подсказка Esc
        esc_text = pygame.font.SysFont("arial", 14).render("ESC - Меню", True, current_theme["text"])
        screen.blit(esc_text, (20, 50))

        # Доска
        start_y = 90
        pygame.draw.rect(screen, current_theme["board"], 
                         (GRID_PADDING, start_y, WIDTH - 2*GRID_PADDING, WIDTH - 2*GRID_PADDING), 
                         border_radius=10)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = board[r][c]
                rect_x = c * TILE_SIZE + (c + 1) * GRID_PADDING
                rect_y = start_y + r * TILE_SIZE + (r + 1) * GRID_PADDING - GRID_PADDING
                
                # Цвет плитки
                color = current_theme["tile_colors"].get(val, current_theme["default_tile"]) if val > 0 else current_theme["empty"]
                pygame.draw.rect(screen, color, (rect_x, rect_y, TILE_SIZE, TILE_SIZE), border_radius=5)
                
                if val > 0:
                    text_color = BLACK if theme_choice == "dark" else (current_theme["text"] if val <= 4 else WHITE)
                    
                    c_font = font_tile
                    if val > 512: c_font = pygame.font.SysFont("arial", 30, bold=True)
                    if val > 9999: c_font = pygame.font.SysFont("arial", 24, bold=True)
                    
                    txt = c_font.render(str(val), True, text_color)
                    txt_rect = txt.get_rect(center=(rect_x + TILE_SIZE/2, rect_y + TILE_SIZE/2))
                    screen.blit(txt, txt_rect)

        if game_over:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(180)
            s.fill(BLACK)
            screen.blit(s, (0,0))
            over_txt = font_tile.render("Game Over!", True, (255, 50, 50))
            screen.blit(over_txt, over_txt.get_rect(center=(WIDTH/2, HEIGHT/2)))
            res_txt = font_score.render("R - Restart, ESC - Menu", True, WHITE)
            screen.blit(res_txt, res_txt.get_rect(center=(WIDTH/2, HEIGHT/2 + 40)))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                board = init_board(GRID_SIZE)
                score = 0
                game_over = False

        pygame.display.flip()
        clock.tick(30)

def main_menu():
    pygame.init()
    # Меню фиксированного размера
    screen = pygame.display.set_mode((400, 500))
    pygame.display.set_caption("2048 Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)
    title_font = pygame.font.SysFont("arial", 50, bold=True)

    # Состояние меню
    selected_size = 4
    selected_theme = "light"
    start_game = False
    
    def set_size(s): nonlocal selected_size; selected_size = s
    def set_theme(t): nonlocal selected_theme; selected_theme = t
    def start(): nonlocal start_game; start_game = True

    while True:
        # Текущая тема меню зависит от выбора
        theme_colors = THEMES[selected_theme]
        screen.fill(theme_colors["bg"])
        
        # Заголовок
        title = title_font.render("2048 GAME", True, theme_colors["text"])
        screen.blit(title, title.get_rect(center=(200, 80)))
        
        # Кнопки
        buttons = [
            # Ряд 1: Размеры
            Button(50, 150, 140, 50, "4 x 4", set_size, 4, selected=(selected_size==4)),
            Button(210, 150, 140, 50, "5 x 5", set_size, 5, selected=(selected_size==5)),
            
            # Ряд 2: Темы
            Button(50, 230, 140, 50, "Light", set_theme, "light", selected=(selected_theme=="light")),
            Button(210, 230, 140, 50, "Dark", set_theme, "dark", selected=(selected_theme=="dark")),
            
            # Старт
            Button(100, 350, 200, 60, "START GAME", start, selected=True)
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for btn in buttons:
                btn.handle_event(event)

        if start_game:
            # Запуск игры, ждем возврата статуса
            status = run_game(selected_size, selected_theme)
            if status == "QUIT":
                pygame.quit()
                sys.exit()
            elif status == "MENU":
                start_game = False
                screen = pygame.display.set_mode((400, 500)) # Возвращаем размер меню
                continue

        for btn in buttons:
            btn.draw(screen, font, theme_colors)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()
