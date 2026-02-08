"""
Advanced CPU Controller with Stealing Phase
Flow: Timing -> Steal Eval -> Greedy Deck -> Combat D&C -> Execute
"""
import random
from game_grid import cell_center
from animations import anim_mgr
from logic_attack import perform_attack_logic

from logic_cpu.dc_combat import select_attack_target, select_position, select_attack_placement

current_turn = 0

def advanced_cpu_turn(grid):
    global current_turn
    current_turn += 1
    
    if anim_mgr.blocking:
        return

    # -----------------------------------------------------------------
    # PHASE 2: COMBAT PHASE (Strict Move OR Attack)
    # -----------------------------------------------------------------
    
    enemy_positions = []
    curr_player_positions = []
    
    for c in range(grid.cols):
        for r in range(grid.rows):
            card = grid.tiles[c][r].card
            if card:
                if card.owner == "enemy":
                    enemy_positions.append((c,r))
                else:
                    curr_player_positions.append((c,r))

    # Evaluate best single action across all cards
    best_action = None
    best_score = -1
    
    print(f"--- CPU TURN START (Turn {current_turn}) ---")
    print(f"CPU evaluating {len(enemy_positions)} units.")

    for e_pos in enemy_positions:
        e_card = grid.tiles[e_pos[0]][e_pos[1]].card
        if not e_card: continue

        # --- OPTION A: ATTACK (from current position) ---
        target_pos = select_attack_target(e_card, e_pos, curr_player_positions, grid)
        attack_obj = None
        attack_score = -1
        
        if target_pos:
            attack_obj = select_attack_placement(e_card, e_pos, target_pos, grid)
            if attack_obj:
                attack_score = attack_obj.dmg
                if attack_obj.element == "fire": attack_score += 2
                
                # Bonus for killing blow
                t_card = grid.tiles[target_pos[0]][target_pos[1]].card
                if t_card and t_card.hp <= attack_obj.dmg:
                    attack_score += 50
        
            print(f"[{current_turn}] Eval ATTACK {e_card.name}: Score={attack_score}")
        
        if attack_score > best_score:
            best_score = attack_score
            best_action = {
                'type': 'ATTACK',
                'card': e_card,
                'pos': e_pos,
                'target': target_pos,
                'attack': attack_obj
            }
            print(f"[{current_turn}] New Best: ATTACK {e_card.name} (Score: {best_score})")

        # --- OPTION B: MOVE (no attack) ---
        # Note: We calculate best move target, but score it lower than a good attack
        # unless it sets up a kill or saves the unit.
        move_target_pos = select_attack_target(e_card, e_pos, curr_player_positions, grid)
        new_pos = select_position(e_card, e_pos, move_target_pos, grid)
        
        move_score = 0
        if new_pos != e_pos:
            move_score = 10 # Base score for moving
            # Add heuristics here if needed (e.g. closer to weak enemy)
        
        print(f"[{current_turn}] Eval MOVE {e_card.name} to {new_pos}: Score={move_score}")

        if move_score > best_score:
            best_score = move_score
            best_action = {
                'type': 'MOVE',
                'card': e_card,
                'pos': e_pos, # Current pos
                'new_pos': new_pos
            }
            print(f"[{current_turn}] New Best: MOVE {e_card.name} (Score: {best_score})")

    # Execute the SINGLE best action
    if best_action:
        print(f"--- EXECUTING BEST ACTION ---")
        if best_action['type'] == 'MOVE':
            card = best_action['card']
            old_pos = best_action['pos']
            new_pos = best_action['new_pos']
            print(f"CPU Action: MOVE {card.name} from {old_pos} to {new_pos}")
            
            # Helper for move animation callback
            def finalize_move(g=grid, old=old_pos, new=new_pos, c=card):
                move_grid_card(g, old, new, c)
                print(f"Move Complete: {c.name}")
                
            anim_mgr.trigger_move_anim(
                cell_center(*old_pos),
                cell_center(*new_pos),
                finalize_move
            )
            anim_mgr.add_floating_text(f"Moving {card.name}", cell_center(*new_pos)[0], cell_center(*new_pos)[1] - 40, (255, 255, 255))
            
        elif best_action['type'] == 'ATTACK':
            card = best_action['card']
            pos = best_action['pos']
            target = best_action['target']
            attack = best_action['attack']
            print(f"[{current_turn}] CPU Action: ATTACK {card.name} at {target} with {attack.name}")
            
            dist = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
            anim_mgr.trigger_attack_anim(
                cell_center(*pos),
                cell_center(*target),
                attack.element,
                lambda ep=pos, tp=target, atk=attack, g=grid, d=dist: perform_attack_logic(
                    ep[0], ep[1], tp[0], tp[1], atk, g, d
                )
            )
            anim_mgr.add_floating_text(f"Attacking!", cell_center(*pos)[0], cell_center(*pos)[1] - 40, (255, 50, 50))
    else:
        print("CPU found no valid actions.")

def move_grid_card(grid, old_pos, new_pos, card):
    grid.tiles[new_pos[0]][new_pos[1]].card = card
    grid.tiles[old_pos[0]][old_pos[1]].card = None
