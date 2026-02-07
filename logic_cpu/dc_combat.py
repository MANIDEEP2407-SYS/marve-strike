"""
D&C Combat Logic: Target, Position, Attack Selection
"""
from logic_cpu.greedy_target_weakest import greedy_best_target
from logic_cpu.greedy_move import greedy_nearest_move

def select_attack_target(attacker_card, attacker_pos, players, grid):
    """
    D&C #1 — Attack Target Selection
    """
    grouped = {}
    for p_pos in players:
        card = grid.tiles[p_pos[0]][p_pos[1]].card
        if not card: continue
        elem = card.element
        if elem not in grouped: grouped[elem] = []
        grouped[elem].append((p_pos, card))
        
    best_targets = []
    for elem, targets in grouped.items():
        best_in_group = min(targets, key=lambda x: x[1].hp)
        best_targets.append(best_in_group)
        
    return greedy_best_target(attacker_pos, players, grid)

def select_position(attacker_card, attacker_pos, target_pos, grid):
    """
    D&C #4 — Position Selection
    """
    if not target_pos:
        return attacker_pos
        
    return greedy_nearest_move(attacker_pos, [target_pos], grid, attacker_card.move_range)

def select_attack_placement(attacker_card, attacker_pos, target_pos, grid):
    """
    D&C #5 — Attack Placement / Zone Evaluation
    """
    if not target_pos: return None
    
    best_attack = None
    max_score = -1
    
    dist = abs(attacker_pos[0] - target_pos[0]) + abs(attacker_pos[1] - target_pos[1])
    
    for atk in attacker_card.attacks:
        if dist <= atk.attack_range:
            score = atk.dmg
            if atk.element == "fire": score += 2
            if score > max_score:
                max_score = score
                best_attack = atk
                
    return best_attack
