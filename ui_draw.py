import pygame
import random
from config import *
from colors import *
from fonts import FONT_BIG, FONT_MAIN
from grid import cell_center
from animations import anim_mgr
from effects import flame_tiles


# -------------------------------------------------
# CONFETTI SYSTEM
# -------------------------------------------------
confetti_particles = []

def spawn_confetti():
    confetti_particles.clear()
    for _ in range(120):
        confetti_particles.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(-HEIGHT, 0),
            "vy": random.uniform(1.5, 4.0),
            "color": random.choice(C_CONFETTI),
            "size": random.randint(4, 7)
        })


def update_and_draw_confetti(screen):
    for p in confetti_particles:
        p["y"] += p["vy"]
        if p["y"] > HEIGHT:
            p["y"] = random.randint(-50, 0)
            p["x"] = random.randint(0, WIDTH)
        pygame.draw.circle(
            screen,
            p["color"],
            (int(p["x"]), int(p["y"])),
            p["size"]
        )


# -------------------------------------------------
# Helper: Card Shape
# -------------------------------------------------
def draw_card_shape(surf, x, y, size, color, is_circle=False):
    rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
    if is_circle:
        pygame.draw.circle(surf, color, (x, y), size // 2)
    else:
        pygame.draw.rect(surf, color, rect, border_radius=12)


# -------------------------------------------------
# MAIN UI DRAW FUNCTION
# -------------------------------------------------
def draw_ui(
    screen,
    grid,
    selected_pos,
    hovered_cell,
    game_state="playing",
    placing_phase=False,
    selected_player_element="fire"
):
    screen.fill(C_BG)

    # =================================================
    # GRID + TILE EFFECTS
    # =================================================
    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, C_GRID, rect, 1)

            # Flame tiles
            for ft in flame_tiles:
                if ft[0] == c and ft[1] == r:
                    alpha = int((ft[2] / (FPS * 3)) * 255)
                    flame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(
                        flame, (*E_FIRE, alpha),
                        (TILE_SIZE // 2, TILE_SIZE // 2),
                        TILE_SIZE // 2
                    )
                    pygame.draw.circle(
                        flame, (255, 200, 50, alpha // 2),
                        (TILE_SIZE // 2, TILE_SIZE // 2),
                        TILE_SIZE // 3
                    )
                    screen.blit(flame, (c * TILE_SIZE, r * TILE_SIZE))

            # Hover highlight
            if (c, r) == hovered_cell:
                s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                s.set_alpha(40)
                s.fill(C_HIGHLIGHT)
                screen.blit(s, (c * TILE_SIZE, r * TILE_SIZE))

            # Move + attack range preview
            if selected_pos:
                sc, sr = selected_pos
                card = grid.tiles[sc][sr].card
                if card and card.owner == "player":
                    dist = abs(sc - c) + abs(sr - r)

                    if dist <= card.move_range:
                        m = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        m.fill((0, 200, 255, 25))
                        screen.blit(m, (c * TILE_SIZE, r * TILE_SIZE))

                    max_range = max(atk.attack_range for atk in card.attacks)
                    if dist <= max_range:
                        a = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        a.fill((255, 255, 0, 18))
                        screen.blit(a, (c * TILE_SIZE, r * TILE_SIZE))

    # =================================================
    # DRAW CARDS
    # =================================================
    for c in range(grid.cols):
        for r in range(grid.rows):
            card = grid.tiles[c][r].card
            if not card:
                continue

            cx, cy = cell_center(c, r)
            base_color = C_PLAYER if card.owner == "player" else C_ENEMY
            draw_card_shape(screen, cx, cy, TILE_SIZE - 10, base_color, True)

            element_colors = {
                "fire": E_FIRE,
                "water": E_WATER,
                "leaf": E_LEAF,
                "null": E_NULL
            }
            pygame.draw.circle(
                screen,
                element_colors.get(card.element, C_WHITE),
                (cx, cy),
                TILE_SIZE // 2 - 6,
                3
            )

            label = f"P{card.index+1}" if card.owner == "player" else f"E{card.index+1}"
            txt = FONT_BIG.render(label, True, C_WHITE)
            screen.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

            # HP bar
            hp_ratio = max(0, card.display_hp / card.max_hp)
            bar_w, bar_h = 70, 9
            hx = cx - bar_w // 2
            hy = cy - TILE_SIZE // 2 - 28
            pygame.draw.rect(screen, (0, 0, 0), (hx, hy, bar_w, bar_h), border_radius=3)
            pygame.draw.rect(
                screen, (0, 200, 0),
                (hx, hy, int(bar_w * hp_ratio), bar_h),
                border_radius=3
            )

            hp_txt = FONT_MAIN.render(str(card.hp), True, C_WHITE)
            screen.blit(hp_txt, (cx - hp_txt.get_width() // 2, hy + 12))

    # =================================================
    # ANIMATIONS
    # =================================================
    anim_mgr.draw(screen)

    # =================================================
    # CONFETTI (VICTORY ONLY)
    # =================================================
    if game_state == "victory":
        if not confetti_particles:
            spawn_confetti()
        update_and_draw_confetti(screen)

    # =================================================
    # BOTTOM INSTRUCTION BAR
    # =================================================
    panel_y = GRID_ROWS * TILE_SIZE
    panel_h = HEIGHT - panel_y

    panel = pygame.Surface((WIDTH, panel_h), pygame.SRCALPHA)
    panel.fill((20, 20, 40, 220))
    screen.blit(panel, (0, panel_y))

    title = FONT_BIG.render("GAME INSTRUCTIONS", True, C_SELECT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 8))

    turn = "ENEMY TURN" if anim_mgr.blocking else "PLAYER TURN"
    turn_color = C_ENEMY if anim_mgr.blocking else C_PLAYER
    turn_txt = FONT_MAIN.render(f"Turn: {turn}", True, turn_color)
    screen.blit(turn_txt, (20, panel_y + 40))

    if placing_phase:
        place_txt = FONT_MAIN.render(
            f"Placement: 1=Fire  2=Water  3=Leaf  4=Null | Selected: {selected_player_element.upper()}",
            True, C_HIGHLIGHT
        )
        screen.blit(place_txt, (20, panel_y + 65))

    controls = [
        "Move: Click Hero → Click Tile",
        "Target Enemy: Hold 1 / 2 / 3",
        "Enemy Turn: Press M"
    ]
    y = panel_y + 95
    for line in controls:
        screen.blit(FONT_MAIN.render(line, True, C_WHITE), (20, y))
        y += 20

    atk_x = WIDTH // 2 + 40
    atk_y = panel_y + 40
    screen.blit(FONT_MAIN.render("Attack Keys", True, C_HIGHLIGHT), (atk_x, atk_y))

    atk_lines = ["Hero 1: Q W E", "Hero 2: A S D", "Hero 3: Z X C"]
    y = atk_y + 25
    for line in atk_lines:
        screen.blit(FONT_MAIN.render(line, True, C_WHITE), (atk_x, y))
        y += 20

    # =================================================
    # END GAME TEXT
    # =================================================
    if game_state == "victory":
        msg = FONT_BIG.render("YOU WIN!", True, C_VICTORY)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
    elif game_state == "defeat":
        msg = FONT_BIG.render("YOU LOSE!", True, C_DEFEAT)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
