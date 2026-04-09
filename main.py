import pygame
import random
import sys
import os

# -------------------
# 资源路径（关键：解决打包问题）
# -------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------
# 配置
# -------------------
SIZE = 4
TILE_SIZE = 120
GAP = 10
WIDTH = SIZE * TILE_SIZE + (SIZE + 1) * GAP
HEIGHT = WIDTH + 100

ANIM_TIME = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Fun Game")

font = pygame.font.SysFont("Segoe UI", 28)
big_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 20)

# -------------------
# 图片加载
# -------------------
images = {}
for i in range(1, 12):
    n = 2**i
    try:
        img = pygame.image.load(resource_path(f"assets/{n}.jpg")).convert_alpha()

        iw, ih = img.get_size()

        scale = max(TILE_SIZE / iw, TILE_SIZE / ih)
        sw, sh = int(iw * scale), int(ih * scale)

        img = pygame.transform.smoothscale(img, (sw, sh))

        x0 = max((sw - TILE_SIZE) // 2, 0)

        y_offset = TILE_SIZE // 6
        y0 = (sh - TILE_SIZE) // 2 - y_offset
        y0 = max(min(y0, sh - TILE_SIZE), 0)

        if sw >= TILE_SIZE and sh >= TILE_SIZE:
            img = img.subsurface((x0, y0, TILE_SIZE, TILE_SIZE)).copy()
        else:
            img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))

        images[n] = img

    except:
        pass

# -------------------
# 动画系统
# -------------------
animations = []

def create_animation(start, end, val):
    animations.append({
        "start": start,
        "end": end,
        "value": val,
        "time": pygame.time.get_ticks()
    })

# -------------------
# 游戏逻辑
# -------------------
def new_board():
    b = [[0]*SIZE for _ in range(SIZE)]
    add_number(b)
    add_number(b)
    return b

def add_number(board):
    empty = [(i,j) for i in range(SIZE) for j in range(SIZE) if board[i][j]==0]
    if empty:
        i,j = random.choice(empty)
        board[i][j] = 2 if random.random()<0.9 else 4

def compress(row):
    new = [x for x in row if x!=0]
    return new + [0]*(SIZE-len(new))

def merge(row):
    score = 0
    for i in range(SIZE-1):
        if row[i]==row[i+1] and row[i]!=0:
            row[i]*=2
            row[i+1]=0
            score+=row[i]
    return row, score

def move_left(board):
    new = []
    score = 0
    for i,row in enumerate(board):
        row = compress(row)
        row, s = merge(row)
        row = compress(row)
        new.append(row)
        score += s
    return new, score

def reverse(b):
    return [r[::-1] for r in b]

def transpose(b):
    return [list(r) for r in zip(*b)]

def move(board, d):
    if d=="LEFT":
        return move_left(board)
    if d=="RIGHT":
        b,s = move_left(reverse(board))
        return reverse(b), s
    if d=="UP":
        b,s = move_left(transpose(board))
        return transpose(b), s
    if d=="DOWN":
        b,s = move_left(reverse(transpose(board)))
        return transpose(reverse(b)), s

def can_move(board):
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j]==0:
                return True
            if j<SIZE-1 and board[i][j]==board[i][j+1]:
                return True
            if i<SIZE-1 and board[i][j]==board[i+1][j]:
                return True
    return False

# -------------------
# 绘制
# -------------------
def draw(board, score, best, game_over):
    # 背景渐变
    for i in range(HEIGHT):
        c = 20 + i//25
        pygame.draw.line(screen, (c,c,c), (0,i), (WIDTH,i))

    # 分数
    pygame.draw.rect(screen, (30,30,30), (0, HEIGHT-100, WIDTH, 100))
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10, HEIGHT-80))
    screen.blit(font.render(f"Best: {best}", True, (255,215,0)), (WIDTH-180, HEIGHT-80))

    # 按钮
    btn = pygame.Rect(WIDTH//2-60, HEIGHT-80, 120, 40)
    pygame.draw.rect(screen, (100,120,255), btn, border_radius=12)
    pygame.draw.rect(screen, (255,255,255), btn, 2, border_radius=12)
    screen.blit(small_font.render("New Game", True, (255,255,255)), (WIDTH//2-45, HEIGHT-70))

    # 网格
    for i in range(SIZE):
        for j in range(SIZE):
            x = GAP + j*(TILE_SIZE+GAP)
            y = GAP + i*(TILE_SIZE+GAP)

            pygame.draw.rect(screen, (50,50,50), (x+4,y+4,TILE_SIZE,TILE_SIZE), border_radius=12)
            pygame.draw.rect(screen, (80,80,80), (x,y,TILE_SIZE,TILE_SIZE), border_radius=12)

            val = board[i][j]
            if val:
                if val in images:
                    screen.blit(images[val], (x,y))
                else:
                    t = big_font.render(str(val), True, (255,255,255))
                    screen.blit(t, (x+30,y+30))

    # 动画
    now = pygame.time.get_ticks()
    for anim in animations[:]:
        t = (now - anim["time"]) / ANIM_TIME
        if t >= 1:
            animations.remove(anim)
            continue

        x = anim["start"][0] + (anim["end"][0]-anim["start"][0]) * t
        y = anim["start"][1] + (anim["end"][1]-anim["start"][1]) * t

        if anim["value"] in images:
            screen.blit(images[anim["value"]], (x,y))

    # Game Over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT-100))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))
        t = big_font.render("Game Over!", True, (255,0,0))
        screen.blit(t,(WIDTH//2-t.get_width()//2, HEIGHT//2-100))

    pygame.display.flip()

# -------------------
# 主循环
# -------------------
def main():
    board = new_board()
    score = 0
    best = 0
    game_over = False

    # 读取最高分
    try:
        with open(resource_path("best_score.txt"), "r") as f:
            best = int(f.read())
    except:
        best = 0

    while True:
        draw(board, score, best, game_over)

        if not can_move(board):
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = new_board()
                    score = 0
                    game_over = False

                if game_over:
                    continue

                direction = None
                if event.key == pygame.K_LEFT:
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    direction = "RIGHT"
                elif event.key == pygame.K_UP:
                    direction = "UP"
                elif event.key == pygame.K_DOWN:
                    direction = "DOWN"

                if direction:
                    new_b, gained = move(board, direction)
                    if new_b != board:
                        board = new_b
                        score += gained
                        best = max(best, score)
                        add_number(board)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if WIDTH//2-60 <= mx <= WIDTH//2+60 and HEIGHT-80 <= my <= HEIGHT-40:
                    board = new_board()
                    score = 0
                    game_over = False

        # 保存最高分（写本地）
        try:
            with open("best_score.txt", "w") as f:
                f.write(str(best))
        except:
            pass

# -------------------
if __name__ == "__main__":
    main()
