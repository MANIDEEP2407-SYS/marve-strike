import random
from grid import cell_center
from animations import anim_mgr
from logic_attack import perform_attack_logic

from logic_cpu.greedy_move import greedy_nearest_move
from logic_cpu.greedy_escape import greedy_escape_move
from logic_cpu.greedy_attack_max import greedy_max_damage_attack
from logic_cpu.greedy_target_weakest import greedy_best_target
from logic_cpu.greedy_element import greedy_element_attack
from logic_cpu.greedy_fire import greedy_fire_spread
from logic_cpu.greedy_heal import greedy_heal_distribution


# --------------------------------------------------
# MOVE CALLBACK
# --------------------------------------------------
def move_callback(grid, e_pos, new_pos, e_card):
    grid.tiles[new_pos[0]][new_pos[1]].card = e_card
    grid.tiles[e_pos[0]][e_pos[1]].card = None


# --------------------------------------------------
# ENEMY PRIORITY (WHO GETS TO ACT)
# --------------------------------------------------
def enemy_priority(e_pos, e_card, players, grid):
    # 1️⃣ Can attack immediately? (highest priority)
    target = greedy_best_target(e_pos, players, grid)
    if target:
        atk = greedy_element_attack(e_card, target, grid)
        dist = abs(e_pos[0] - target[0]) + abs(e_pos[1] - target[1])
        if dist <= atk.attack_range:
            return 1000

    # 2️⃣ Low HP enemies must react
    hp_factor = 1 - (e_card.hp / e_card.max_hp)

    # 3️⃣ Distance to nearest player
    min_dist = min(abs(e_pos[0] - p[0]) + abs(e_pos[1] - p[1]) for p in players)

    return hp_factor * 100 + (10 / max(min_dist, 1))


# --------------------------------------------------
# MOVE SCORE
# --------------------------------------------------
def calculate_move_score(e_pos, players, grid, e_card):
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not players:
        return -10

    current_dist = min(dist(e_pos, p) for p in players)

    if e_card.element in ["water", "leaf"]:
        new_pos = greedy_escape_move(e_pos, players, grid)
    else:
        new_pos = greedy_nearest_move(e_pos, players, grid)

    # ❌ useless movement
    if new_pos == e_pos:
        return -5

    new_dist = min(dist(new_pos, p) for p in players)

    # 🧱 border penalty
    edge_penalty = 2 if (
        new_pos[0] in (0, grid.cols - 1) or
        new_pos[1] in (0, grid.rows - 1)
    ) else 0

    return (current_dist - new_dist) - edge_penalty


# --------------------------------------------------
# ATTACK SCORE
# --------------------------------------------------
def calculate_attack_score(e_card, players, grid, e_pos):
    target_pos = greedy_best_target(e_pos, players, grid)
    if not target_pos:
        return -10

    target_card = grid.tiles[target_pos[0]][target_pos[1]].card
    atk = greedy_element_attack(e_card, target_pos, grid)

    dist = abs(e_pos[0] - target_pos[0]) + abs(e_pos[1] - target_pos[1])
    if dist > atk.attack_range:
        return -5

    dmg = atk.dmg
    health_factor = 1 - (target_card.hp / target_card.max_hp)
    kill_bonus = 15 if dmg >= target_card.hp else 0

    return dmg * (1 + health_factor) + kill_bonus


# --------------------------------------------------
# CPU TURN
# --------------------------------------------------
def cpu_turn(grid):
    if anim_mgr.blocking:
        return

    enemies = []
    players = []

    # Collect units
    for c in range(grid.cols):
        for r in range(grid.rows):
            card = grid.tiles[c][r].card
            if not card:
                continue
            if card.owner == "enemy":
                enemies.append((c, r))
            else:
                players.append((c, r))

    if not players or not enemies:
        return

    # ✅ PICK BEST ENEMY (FIXES CORNER LOCK)
    best_enemy = None
    best_score = -9999

    for e_pos in enemies:
        e_card = grid.tiles[e_pos[0]][e_pos[1]].card
        score = enemy_priority(e_pos, e_card, players, grid)
        if score > best_score:
            best_score = score
            best_enemy = e_pos

    if not best_enemy:
        return

    e_pos = best_enemy
    e_card = grid.tiles[e_pos[0]][e_pos[1]].card

    move_score = calculate_move_score(e_pos, players, grid, e_card)
    attack_score = calculate_attack_score(e_card, players, grid, e_pos)

    # 🔥 Emergency response if attacked
    if e_card.hp < e_card.max_hp * 0.6:
        attack_score += 8

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------
    if attack_score > move_score + 1:
        target_pos = greedy_best_target(e_pos, players, grid)
        if not target_pos:
            return

        atk = greedy_element_attack(e_card, target_pos, grid)
        dist = abs(e_pos[0] - target_pos[0]) + abs(e_pos[1] - target_pos[1])

        if dist <= atk.attack_range:
            anim_mgr.trigger_attack_anim(
                cell_center(*e_pos),
                cell_center(*target_pos),
                atk.element,
                lambda: perform_attack_logic(
                    e_pos[0], e_pos[1],
                    target_pos[0], target_pos[1],
                    atk, grid, dist
                )
            )
            return

    # --------------------------------------------------
    # MOVE
    # --------------------------------------------------
    if e_card.element in ["water", "leaf"]:
        new_pos = greedy_escape_move(e_pos, players, grid)
    else:
        new_pos = greedy_nearest_move(e_pos, players, grid)

    if new_pos != e_pos:
        anim_mgr.trigger_move_anim(
            cell_center(*e_pos),
            cell_center(*new_pos),
            lambda: move_callback(grid, e_pos, new_pos, e_card)
        )
