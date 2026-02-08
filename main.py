import pygame
import random

from config import *
from game_grid import Grid, cell_center
from animations import anim_mgr
from effects import (
    flame_tiles, regen_effects, burn_effects,
    process_flame_tiles, process_regen, process_burn
)
from logic_attack import initiate_player_attack
from logic_cpu.advanced_cpu import advanced_cpu_turn as cpu_turn
from ui_draw import draw_ui, spawn_confetti, update_and_draw_confetti, draw_help_overlay
from card import Card
from attack import Attack
from colors import *
from fonts import *
import math

pygame.init()
pygame.display.set_caption("Card Strike: Elemental GUI")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# -------------------------------------------------
# GAME STATE
# -------------------------------------------------
grid = Grid(GRID_COLS, GRID_ROWS)

selected_pos = None
hovered_cell = (0, 0)

placing_phase = True
placed_count = 0
cpu_pending = False
show_help = False

# Player variant selection during placement
selected_player_element = "fire"  # default

# -------------------------------------------------
# CARD FACTORIES
# -------------------------------------------------
def create_player_card(slot_index: int, element: str) -> Card:
    if element == "fire":
        attacks = [
            Attack("Burning Trail", 12, "fire", 5),
            Attack("Fire Claw", 14, "fire", 4),
            Attack("Inferno Burst", 16, "fire", 5),
        ]
    elif element == "water":
        attacks = [
            Attack("Water Lash", 10, "water", 5),
            Attack("Tidal Push", 12, "water", 4),
            Attack("Healing Wave", 8, "water", 4),
        ]
    elif element == "leaf":
        attacks = [
            Attack("Nature's Embrace", 10, "leaf", 4),
            Attack("Vine Whip", 12, "leaf", 5),
            Attack("Thorn Burst", 14, "leaf", 4),
        ]
    else:  # null
        attacks = [
            Attack("Strike", 12, "null", 4),
            Attack("Guard Break", 14, "null", 4),
            Attack("Focused Blow", 16, "null", 3),
        ]

    card = Card(
        owner="player",
        name=f"Hero {slot_index+1}",
        hp=100,
        max_hp=100,
        attacks=attacks,
        move_range=3,
        element=element,
        index=slot_index
    )
    card.display_hp = card.hp
    return card


def create_enemy_card(slot_index: int) -> Card:
    e = random.choice(["fire", "water", "leaf", "null"])
    if e == "fire":
        attacks = [
            Attack("Burning Trail", 12, "fire", 5),
            Attack("Fire Claw", 14, "fire", 4),
            Attack("Inferno Burst", 16, "fire", 5),
        ]
    elif e == "water":
        attacks = [
            Attack("Water Lash", 10, "water", 5),
            Attack("Tidal Push", 12, "water", 4),
            Attack("Healing Wave", 8, "water", 4),
        ]
    elif e == "leaf":
        attacks = [
            Attack("Nature's Embrace", 10, "leaf", 4),
            Attack("Vine Whip", 12, "leaf", 5),
            Attack("Thorn Burst", 14, "leaf", 4),
        ]
    else:  # null
        attacks = [
            Attack("Strike", 12, "null", 4),
            Attack("Guard Break", 14, "null", 4),
            Attack("Focused Blow", 16, "null", 3),
        ]
    card = Card(
        owner="enemy",
        name=f"Beast {slot_index+1}",
        hp=100,
        max_hp=100,
        attacks=attacks,
        move_range=2,
        element=e,
        index=slot_index
    )
    card.display_hp = card.hp
    return card


def check_win_lose(grid):
    player_alive = any(
        tile.card and tile.card.owner == "player"
        for col in grid.tiles for tile in col
    )
    enemy_alive = any(
        tile.card and tile.card.owner == "enemy"
        for col in grid.tiles for tile in col
    )
    if not enemy_alive:
        return "victory"
    if not player_alive:
        return "defeat"
    return "playing"


# -------------------------------------------------
# STEALING PHASE SETUP
# -------------------------------------------------
from stealing_phase import StealingPhase
stealing_phase = StealingPhase(screen)
stealing_phase_active = True
player_final_cards = []
cpu_final_cards = []

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
game_state = "playing"
running = True

while running:
    clock.tick(FPS)
    # -----------------------------
    # STEALING PHASE (runs first)
    # -----------------------------
    if stealing_phase_active:
        stealing_phase.draw()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEMOTION:
                stealing_phase.handle_mouse_move(pygame.mouse.get_pos())
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                stealing_phase.handle_click(pygame.mouse.get_pos())
            
            if event.type == pygame.USEREVENT + 1:  # CPU timer
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop timer
                stealing_phase.cpu_turn()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if stealing_phase.phase_complete:
                    # Get final decks and switch to placement
                    player_final_cards, cpu_final_cards = stealing_phase.get_final_decks()
                    stealing_phase_active = False
                    placing_phase = True
        
        continue  # Skip rest of loop during stealing phase

    # -----------------------------
    # UPDATE LOGIC
    # -----------------------------
    anim_mgr.update()
    process_flame_tiles(grid)
    process_regen()
    process_burn(grid)

    if cpu_pending and not anim_mgr.blocking and not placing_phase:
        cpu_pending = False
        cpu_turn(grid)
        game_state = check_win_lose(grid)

    mx, my = pygame.mouse.get_pos()
    hovered_cell = (mx // TILE_SIZE, my // TILE_SIZE)

    # -----------------------------
    # EVENTS
    # -----------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------------------------------
        # PLAYER ELEMENT SELECTION (PLACEMENT)
        # ---------------------------------
        if event.type == pygame.KEYDOWN and placing_phase:
            if event.key == pygame.K_1:
                selected_player_element = "fire"
            elif event.key == pygame.K_2:
                selected_player_element = "water"
            elif event.key == pygame.K_3:
                selected_player_element = "leaf"
            elif event.key == pygame.K_4:
                selected_player_element = "null"

        # ---------------------------------
        # HELP TOGGLE (H key)
        # ---------------------------------
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            show_help = not show_help

        # ---------------------------------
        # MOUSE CLICK
        # ---------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and not anim_mgr.blocking:
            c, r = hovered_cell
            if not grid.in_bounds(c, r):
                continue

            if placing_phase:
                if grid.tiles[c][r].card is None and placed_count < len(player_final_cards):
                    # Use card from stealing phase if available
                    if player_final_cards:
                        grid.tiles[c][r].card = player_final_cards[placed_count]
                    else:
                        grid.tiles[c][r].card = create_player_card(
                            placed_count, selected_player_element
                        )
                    placed_count += 1
                    anim_mgr.add_particle(*cell_center(c, r), "leaf")

                    if placed_count >= 3:
                        placing_phase = False
                        empties = [
                            (x, y)
                            for x in range(GRID_COLS)
                            for y in range(GRID_ROWS)
                            if not grid.tiles[x][y].card
                        ]
                        # Place CPU cards from stealing phase
                        for i, cpu_card in enumerate(cpu_final_cards):
                            if empties:
                                ex, ey = random.choice(empties)
                                grid.tiles[ex][ey].card = cpu_card
                                empties.remove((ex, ey))

            else:
                clicked = grid.tiles[c][r].card
                if clicked and clicked.owner == "player":
                    selected_pos = (c, r)
                elif selected_pos:
                    sc, sr = selected_pos
                    mover = grid.tiles[sc][sr].card
                    if mover:
                        dist = abs(c - sc) + abs(r - sr)
                        if dist <= mover.move_range and not clicked:
                            grid.tiles[c][r].card = mover
                            grid.tiles[sc][sr].card = None
                            selected_pos = None
                            anim_mgr.add_particle(*cell_center(c, r), "air")
                            cpu_pending = True

        # ---------------------------------
        # COMBAT KEYS
        # ---------------------------------
        if event.type == pygame.KEYDOWN and not placing_phase and not anim_mgr.blocking:
            if event.key == pygame.K_m:
                cpu_turn(grid)

            controls = {
                pygame.K_q: (0, 0), pygame.K_w: (0, 1), pygame.K_e: (0, 2),
                pygame.K_a: (1, 0), pygame.K_s: (1, 1), pygame.K_d: (1, 2),
                pygame.K_z: (2, 0), pygame.K_x: (2, 1), pygame.K_c: (2, 2),
            }

            if event.key in controls:
                pid, aid = controls[event.key]
                keys = pygame.key.get_pressed()
                target_idx = (
                    0 if keys[pygame.K_1]
                    else 1 if keys[pygame.K_2]
                    else 2 if keys[pygame.K_3]
                    else -1
                )

                if target_idx != -1:
                    initiate_player_attack(pid, aid, target_idx, grid)
                    cpu_pending = True
                else:
                    anim_mgr.add_floating_text(
                        "Hold 1/2/3!", mx, my, (255, 255, 0)
                    )

    # -----------------------------
    # DRAW
    # -----------------------------
    draw_ui(
        screen,
        grid,
        selected_pos,
        hovered_cell,
        placing_phase,
        selected_player_element
    )

    # Help overlay
    if show_help and game_state == "playing":
        draw_help_overlay(screen)

    if game_state != "playing":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        _finish_frame = getattr(pygame, '_finish_frame', 0) + 1
        pygame._finish_frame = _finish_frame

        if game_state == "victory":
            # ── Confetti ──
            if _finish_frame == 1:
                spawn_confetti()
            update_and_draw_confetti(screen)

            # Title glow
            pulse = 0.8 + 0.2 * math.sin(_finish_frame * 0.06)
            glow_a = int(60 * pulse)
            title_text = "VICTORY"
            title_color = C_VICTORY
            icon_text = "★"
        else:
            title_text = "DEFEAT"
            title_color = C_DEFEAT
            icon_text = "✕"
            # Ash particles for defeat
            for _ in range(2):
                ax = random.randint(0, WIDTH)
                ay = random.randint(0, HEIGHT)
                ash_a = random.randint(20, 60)
                pygame.draw.circle(screen, (*C_TEXT_DIM, ash_a), (ax, ay), random.randint(1, 3))

        # ── Trophy / Skull icon ──
        icon_surf = FONT_HERO.render(icon_text, True, title_color)
        screen.blit(icon_surf, (WIDTH // 2 - icon_surf.get_width() // 2, HEIGHT // 2 - 180))

        # ── Title text with shadow ──
        shadow = FONT_HERO.render(title_text, True, C_SHADOW)
        screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 4, HEIGHT // 2 - 90 + 4))
        txt_surf = FONT_HERO.render(title_text, True, title_color)
        screen.blit(txt_surf, (WIDTH // 2 - txt_surf.get_width() // 2, HEIGHT // 2 - 90))

        # ── Stats panel ──
        panel_w, panel_h = 400, 120
        px = WIDTH // 2 - panel_w // 2
        py = HEIGHT // 2 + 20
        panel_rect = pygame.Rect(px, py, panel_w, panel_h)
        pygame.draw.rect(screen, (*C_BG_TERTIARY, 220), panel_rect, border_radius=RADIUS_MD)
        pygame.draw.rect(screen, C_ACCENT_DARK, panel_rect, 2, border_radius=RADIUS_MD)

        p_alive = sum(1 for col in grid.tiles for tile in col if tile.card and tile.card.owner == "player")
        e_alive = sum(1 for col in grid.tiles for tile in col if tile.card and tile.card.owner == "enemy")
        stat1 = FONT_MAIN.render(f"Your Units Alive: {p_alive}", True, C_PLAYER_GLOW)
        stat2 = FONT_MAIN.render(f"Enemy Units Alive: {e_alive}", True, C_ENEMY_GLOW)
        screen.blit(stat1, (px + 24, py + 24))
        screen.blit(stat2, (px + 24, py + 60))

        # ── PLAY AGAIN button ──
        btn_w, btn_h = 280, 56
        btn_x = WIDTH // 2 - btn_w // 2
        btn_y = HEIGHT // 2 + 170
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        btn_hov = btn_rect.collidepoint(pygame.mouse.get_pos())
        btn_color = C_ACCENT_GLOW if btn_hov else C_ACCENT
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=RADIUS_MD)
        pygame.draw.rect(screen, C_GOLD if btn_hov else C_ACCENT_DARK, btn_rect, 3, border_radius=RADIUS_MD)
        btn_text = FONT_BIG.render("PLAY AGAIN", True, C_TEXT)
        screen.blit(btn_text, (btn_x + (btn_w - btn_text.get_width()) // 2, btn_y + 12))

        # Handle restart click
        for ev in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if btn_rect.collidepoint(ev.pos):
                # Reset everything
                grid = Grid(GRID_COLS, GRID_ROWS)
                selected_pos = None
                placing_phase = True
                placed_count = 0
                cpu_pending = False
                game_state = "playing"
                show_help = False
                stealing_phase.reset()
                stealing_phase_active = True
                player_final_cards = []
                cpu_final_cards = []
                anim_mgr.blocking = False
                pygame._finish_frame = 0

        anim_mgr.blocking = True

    pygame.display.flip()

pygame.quit()
