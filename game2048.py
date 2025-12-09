import pygame
import random
import sys

# --- Константы и настройки ---
WIDTH, HEIGHT = 400, 500  # Высота больше для отображения счета
GRID_SIZE = 4
TILE_SIZE = 80
GRID_PADDING = 10
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
FONT_COLOR_DARK = (119, 110, 101)
FONT_COLOR_LIGHT = (249, 246, 242)

# Цвета для плиток (как в оригинальной игре) [web:2][web:1]
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# --- Логика игры ---

def init_board():
    """Создает пустую доску 4x4 и добавляет две стартовые плитки."""
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    add_new_tile(board)
    add_new_tile(board)
    return board

def add_new_tile(board):
    """Добавляет 2 (90%) или 4 (10%) в случайную пустую ячейку."""
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 4 if random.random() > 0.9 else 2

def compress(board):
    """Сдвигает все плитки влево, убирая нули."""
    new_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r in range(GRID_SIZE):
        pos = 0
        for c in range(GRID_SIZE):
            if board[r][c] != 0:
                new_board[r][pos] = board[r][c]
                pos += 1
    return new_board

def merge(board, score):
    """Объединяет одинаковые плитки при сдвиге влево."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if board[r][c] != 0 and board[r][c] == board[r][c + 1]:
                board[r][c] *= 2
                board[r][c + 1] = 0
                score += board[r][c]
    return board, score

def reverse(board):
    """Зеркально отражает доску (для движения вправо)."""
    new_board = []
    for r in range(GRID_SIZE):
        new_board.append([])
        for c in range(GRID_SIZE):
            new_board[r].append(board[r][GRID_SIZE - 1 - c])
    return new_board

def transpose(board):
    """Транспонирует матрицу (обмен строк и столбцов, для движения вверх/вниз)."""
    new_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            new_board[r][c] = board[c][r]
    return new_board

def move_left(board, score):
    board = compress(board)
    board, score = merge(board, score)
    board = compress(board)
    return board, score

def move_right(board, score):
    board = reverse(board)
    board, score = move_left(board, score)
    board = reverse(board)
    return board, score

def move_up(board, score):
    board = transpose(board)
    board, score = move_left(board, score)
    board = transpose(board)
    return board, score

def move_down(board, score):
    board = transpose(board)
    board, score = move_right(board, score)
    board = transpose(board)
    return board, score

def check_game_over(board):
    """Проверяет, есть ли возможные ходы."""
    # Если есть нули, игра не окончена
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == 0:
                return False
    # Проверка на возможность слияния по горизонтали и вертикали
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if board[r][c] == board[r][c + 1]:
                return False
            if board[c][r] == board[c + 1][r]: # Проверка столбцов (транспонированная логика)
                return False
    return True

# --- Графический интерфейс ---

def draw_board(screen, board, score, font_score, font_tile):
    screen.fill(BACKGROUND_COLOR)
    
    # Отображение счета
    score_text = font_score.render(f"Score: {score}", True, FONT_COLOR_LIGHT)
    screen.blit(score_text, (20, 20))

    # Рисование сетки
    start_y = 80 # Сдвиг вниз для места под счет
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = board[r][c]
            rect_x = c * TILE_SIZE + (c + 1) * GRID_PADDING
            rect_y = start_y + r * TILE_SIZE + (r + 1) * GRID_PADDING
            
            # Выбор цвета
            color = TILE_COLORS.get(val, TILE_COLORS[2048]) if val > 0 else EMPTY_TILE_COLOR
            pygame.draw.rect(screen, color, (rect_x, rect_y, TILE_SIZE, TILE_SIZE), border_radius=5)
            
            if val > 0:
                text_color = FONT_COLOR_DARK if val <= 4 else FONT_COLOR_LIGHT
                # Уменьшаем шрифт для больших чисел
                current_font = font_tile
                if val > 512:
                    current_font = pygame.font.SysFont("arial", 30, bold=True)
                
                text = current_font.render(str(val), True, text_color)
                text_rect = text.get_rect(center=(rect_x + TILE_SIZE/2, rect_y + TILE_SIZE/2))
                screen.blit(text, text_rect)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 на Pygame")
clock = pygame.time.Clock()
    
# Шрифты
font_score = pygame.font.SysFont("arial", 30, bold=True)
font_tile = pygame.font.SysFont("arial", 40, bold=True)

board = init_board()
score = 0
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN and not game_over:
            # Сохраняем старую доску для проверки изменений
            # Важно сделать глубокую копию, но для списка списков int достаточно list comprehensions
            old_board = [row[:] for row in board]
            moved = False
                
            if event.key == pygame.K_LEFT:
                board, score = move_left(board, score)
            elif event.key == pygame.K_RIGHT:
                board, score = move_right(board, score)
            elif event.key == pygame.K_UP:
                board, score = move_up(board, score)
            elif event.key == pygame.K_DOWN:
                board, score = move_down(board, score)
            elif event.key == pygame.K_r: # Рестарт
                board = init_board()
                score = 0
                
            # Если доска изменилась, добавляем новую плитку
            if old_board != board:
                add_new_tile(board)
                if check_game_over(board):
                    game_over = True
                    print("Game Over!")

    draw_board(screen, board, score, font_score, font_tile)
        
    if game_over:
        # Затемнение экрана при проигрыше
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(128)
        s.fill((255, 230, 150)) # Желтоватый оттенок конца игры [web:2]
        screen.blit(s, (0,0))
        over_text = font_score.render("Game Over!", True, FONT_COLOR_DARK)
        rect = over_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(over_text, rect)
        restart_text = pygame.font.SysFont("arial", 20).render("Нажми R для рестарта", True, FONT_COLOR_DARK)
        rect_res = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 40))
        screen.blit(restart_text, rect_res)
            
        # Обработка рестарта в состоянии Game Over
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            board = init_board()
            score = 0
            game_over = False

    pygame.display.flip()
    clock.tick(30)