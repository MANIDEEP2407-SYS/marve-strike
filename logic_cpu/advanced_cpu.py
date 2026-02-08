"""
Advanced CPU Controller — Minimax D&C AI with Greedy Fallback
Flow: Minimax Look-Ahead → Execute Best Action → Animate
"""
import random
from game_grid import cell_center
from animations import anim_mgr
from logic_attack import perform_attack_logic

from logic_cpu.dc_combat import select_attack_target, select_position, select_attack_placement
from logic_cpu.minimax import minimax_best_action

current_turn = 0

def advanced_cpu_turn(grid):
    global current_turn
    current_turn += 1
    
    if anim_mgr.blocking:
        return

    print(f"\n=== CPU TURN {current_turn} (MINIMAX D&C) ===")

    # -----------------------------------------------------------------
    # PHASE 1: MINIMAX DECISION (Divide & Conquer)
    # -----------------------------------------------------------------
    best_action = None
    try:
        best_action = minimax_best_action(grid, depth=2)
    except Exception as e:
        print(f"[MINIMAX] Error: {e} — falling back to greedy")
        best_action = None

    # -----------------------------------------------------------------
    # PHASE 2: GREEDY FALLBACK (if Minimax finds nothing)
    # -----------------------------------------------------------------
    if not best_action:
        print("[CPU] Minimax returned None, using greedy fallback...")
        best_action = _greedy_fallback(grid)

    # -----------------------------------------------------------------
    # PHASE 3: EXECUTE the chosen action
    # -----------------------------------------------------------------
    if best_action:
        _execute_action(best_action, grid)
    else:
        print("[CPU] No valid actions found at all.")


def _greedy_fallback(grid):
    """Original greedy logic as safety net."""
    enemy_positions = []
    player_positions = []
    
    for c in range(grid.cols):
        for r in range(grid.rows):
            card = grid.tiles[c][r].card
            if card:
                if card.owner == "enemy":
                    enemy_positions.append((c, r))
                else:
                    player_positions.append((c, r))

    best_action = None
    best_score = -1

    for e_pos in enemy_positions:
        e_card = grid.tiles[e_pos[0]][e_pos[1]].card
        if not e_card:
            continue

        # OPTION A: ATTACK
        target_pos = select_attack_target(e_card, e_pos, player_positions, grid)
        if target_pos:
            attack_obj = select_attack_placement(e_card, e_pos, target_pos, grid)
            if attack_obj:
                score = attack_obj.dmg
                if attack_obj.element == "fire":
                    score += 2
                t_card = grid.tiles[target_pos[0]][target_pos[1]].card
                if t_card and t_card.hp <= attack_obj.dmg:
                    score += 50
                if score > best_score:
                    best_score = score
                    best_action = {
                        'type': 'ATTACK',
                        'unit_pos': e_pos,
                        'target_pos': target_pos,
                        'attack': attack_obj,
                        'dist': abs(e_pos[0] - target_pos[0]) + abs(e_pos[1] - target_pos[1]),
                    }

        # OPTION B: MOVE
        move_target = select_attack_target(e_card, e_pos, player_positions, grid)
        new_pos = select_position(e_card, e_pos, move_target, grid)
        if new_pos != e_pos:
            score = 10
            if score > best_score:
                best_score = score
                best_action = {
                    'type': 'MOVE',
                    'unit_pos': e_pos,
                    'new_pos': new_pos,
                }

    return best_action


def _execute_action(action, grid):
    """Execute the chosen action with proper animations."""
    if action['type'] == 'MOVE':
        old_pos = action['unit_pos']
        new_pos = action['new_pos']
        card = grid.tiles[old_pos[0]][old_pos[1]].card
        if not card:
            return
        print(f"[CPU] MOVE {card.name} from {old_pos} to {new_pos}")
        
        def finalize_move(g=grid, old=old_pos, new=new_pos, c=card):
            move_grid_card(g, old, new, c)
            
        anim_mgr.trigger_move_anim(
            cell_center(*old_pos),
            cell_center(*new_pos),
            finalize_move
        )
        anim_mgr.add_floating_text(
            f"Moving {card.name}",
            cell_center(*new_pos)[0],
            cell_center(*new_pos)[1] - 40,
            (255, 255, 255)
        )
        
    elif action['type'] == 'ATTACK':
        pos = action['unit_pos']
        target = action['target_pos']
        atk = action['attack']
        card = grid.tiles[pos[0]][pos[1]].card
        if not card:
            return
        dist = action.get('dist', abs(pos[0] - target[0]) + abs(pos[1] - target[1]))
        print(f"[CPU] ATTACK {card.name} → {target} with {atk.name} (dist={dist})")
        
        anim_mgr.trigger_attack_anim(
            cell_center(*pos),
            cell_center(*target),
            atk.element,
            lambda ep=pos, tp=target, a=atk, g=grid, d=dist: perform_attack_logic(
                ep[0], ep[1], tp[0], tp[1], a, g, d
            )
        )
        anim_mgr.add_floating_text(
            "Attacking!",
            cell_center(*pos)[0],
            cell_center(*pos)[1] - 40,
            (255, 50, 50)
        )


def move_grid_card(grid, old_pos, new_pos, card):
    grid.tiles[new_pos[0]][new_pos[1]].card = card
    grid.tiles[old_pos[0]][old_pos[1]].card = None
