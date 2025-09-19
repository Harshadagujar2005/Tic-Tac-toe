# fancy_tictactoe_fixed.py
import pygame, sys, math, time
pygame.init()

# Window / board sizes
BOARD_PIX = 600               # board area (600x600)
PANEL_H = 120                 # bottom panel for status + buttons
WIN_W = BOARD_PIX
WIN_H = BOARD_PIX + PANEL_H

# Derived
ROWS = COLS = 3
S = BOARD_PIX // 3            # square size

# Visual params
LINE_COLOR = (30,30,30)
BG_COLOR = (245,245,245)
CIRCLE_COLOR = (0,180,0)     # O color (green)
CROSS_COLOR = (200,40,40)    # X color (red)
WIN_LINE_COLOR = (10,150,10)
BUTTON_COLOR = (10,10,160)
BUTTON_TEXT_COLOR = (255,255,255)
STATUS_TEXT_COLOR = (25,25,25)

LINE_W = 8
CIRCLE_W = 12
CROSS_W = 18
CIRCLE_R = S//3

# Fonts
FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 48, bold=True)

# Pygame window
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Tic-Tac-Toe AI (fixed)")

# Restart button area
BTN_W, BTN_H = 160, 50
BTN_X = WIN_W//2 - BTN_W//2
BTN_Y = BOARD_PIX + 40
restart_rect = pygame.Rect(BTN_X, BTN_Y, BTN_W, BTN_H)

# Game state
def empty_board():
    return [['' for _ in range(COLS)] for _ in range(ROWS)]

board = empty_board()
human, ai = 'X', 'O'
game_over = False
winner = None
win_line = None   # ((c1,r1),(c2,r2))

# --------- Pure board helpers (no globals) ----------
def check_winner_board(bd):
    # returns ('X'/'O', ((c1,r1),(c2,r2))) or (None, None) or ('Draw', None)
    # rows
    for r in range(3):
        if bd[r][0] != '' and bd[r][0] == bd[r][1] == bd[r][2]:
            return bd[r][0], ((0,r),(2,r))
    # cols
    for c in range(3):
        if bd[0][c] != '' and bd[0][c] == bd[1][c] == bd[2][c]:
            return bd[0][c], ((c,0),(c,2))
    # diagonals
    if bd[0][0] != '' and bd[0][0] == bd[1][1] == bd[2][2]:
        return bd[0][0], ((0,0),(2,2))
    if bd[0][2] != '' and bd[0][2] == bd[1][1] == bd[2][0]:
        return bd[0][2], ((2,0),(0,2))
    # draw?
    if all(bd[r][c] != '' for r in range(3) for c in range(3)):
        return 'Draw', None
    return None, None

def available_moves_board(bd):
    return [(r,c) for r in range(3) for c in range(3) if bd[r][c] == '']

# ---------- Minimax with alpha-beta (pure) --------------
def minimax(bd, depth, is_maximizing, alpha, beta):
    res, _ = check_winner_board(bd)
    if res == ai:
        return 10 - depth
    if res == human:
        return -10 + depth
    if res == 'Draw':
        return 0

    if is_maximizing:
        best = -9999
        for (r,c) in available_moves_board(bd):
            bd[r][c] = ai
            val = minimax(bd, depth+1, False, alpha, beta)
            bd[r][c] = ''
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = 9999
        for (r,c) in available_moves_board(bd):
            bd[r][c] = human
            val = minimax(bd, depth+1, True, alpha, beta)
            bd[r][c] = ''
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def best_move_board(bd):
    best_score = -9999
    move = None
    for (r,c) in available_moves_board(bd):
        bd[r][c] = ai
        score = minimax(bd, 0, False, -9999, 9999)
        bd[r][c] = ''
        if score > best_score:
            best_score = score
            move = (r,c)
    return move

# --------------- Drawing ----------------
def draw_grid():
    # background
    screen.fill(BG_COLOR)
    # two horizontal and vertical lines inside the BOARD_PIX square
    for i in range(1,3):
        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, i*S), (BOARD_PIX, i*S), LINE_W)
        # vertical
        pygame.draw.line(screen, LINE_COLOR, (i*S, 0), (i*S, BOARD_PIX), LINE_W)

def draw_figures():
    for r in range(3):
        for c in range(3):
            cx = c*S + S//2
            cy = r*S + S//2
            if board[r][c] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, (cx, cy), CIRCLE_R, CIRCLE_W)
            elif board[r][c] == 'X':
                offset = S//4
                pygame.draw.line(screen, CROSS_COLOR, (cx-offset, cy-offset), (cx+offset, cy+offset), CROSS_W)
                pygame.draw.line(screen, CROSS_COLOR, (cx-offset, cy+offset), (cx+offset, cy-offset), CROSS_W)

def draw_winline():
    if win_line is None:
        return
    (c1,r1), (c2,r2) = win_line
    start = (c1*S + S//2, r1*S + S//2)
    end   = (c2*S + S//2, r2*S + S//2)
    pygame.draw.line(screen, WIN_LINE_COLOR, start, end, 12)

def draw_panel():
    # button
    pygame.draw.rect(screen, BUTTON_COLOR, restart_rect, border_radius=12)
    btxt = FONT.render("Restart", True, BUTTON_TEXT_COLOR)
    screen.blit(btxt, (restart_rect.x + (BTN_W - btxt.get_width())//2, restart_rect.y + (BTN_H - btxt.get_height())//2))
    # status text
    if game_over:
        if winner == 'Draw' or winner is None:
            msg = "Draw!"
        else:
            msg = f"{winner} Wins!"
        rt = BIG_FONT.render(msg, True, (80,20,20))
        screen.blit(rt, (20, BOARD_PIX + 10))
    else:
        msg = f"Your move ({human})"
        rt = FONT.render(msg, True, STATUS_TEXT_COLOR)
        screen.blit(rt, (20, BOARD_PIX + 20))

# ------------- Game actions ----------------
def restart():
    global board, game_over, winner, win_line
    board = empty_board()
    game_over = False
    winner = None
    win_line = None

# --------------- Main loop -----------------
clock = pygame.time.Clock()
running = True

# If you want debugging prints to console:
# print("Game started. Click inside the top 600x600 area to play.")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # click restart?
            if restart_rect.collidepoint(mx, my):
                restart()
                continue
            # click inside board?
            if my < BOARD_PIX and not game_over:
                r = my // S
                c = mx // S
                if board[r][c] == '':
                    board[r][c] = human
                    # check terminal
                    res, line = check_winner_board(board)
                    if res is not None:
                        game_over = True
                        winner = res
                        win_line = line
                    else:
                        # AI turn
                        pygame.display.update()
                        pygame.time.delay(150)    # small pause for realism
                        mv = best_move_board(board)
                        if mv:
                            board[mv[0]][mv[1]] = ai
                        # check again
                        res2, line2 = check_winner_board(board)
                        if res2 is not None:
                            game_over = True
                            winner = res2
                            win_line = line2

    # draw everything
    draw_grid()
    draw_figures()
    draw_winline()
    draw_panel()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
