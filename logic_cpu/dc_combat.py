"""
D&C Combat Logic: Target, Position, Attack Selection
"""
from logic_cpu.greedy_target_weakest import greedy_best_target
from logic_cpu.greedy_move import greedy_nearest_move

def select_attack_target(attacker_card, attacker_pos, players, grid):
    """
    D&C #1 — Attack Target Selection
    Divide targets by element group, conquer by finding weakest in each,
    then delegate final pick to greedy scoring.
    """
    # Divide: group player positions by element
    grouped = {}
    for p_pos in players:
        card = grid.tiles[p_pos[0]][p_pos[1]].card
        if not card:
            continue
        elem = card.element
        if elem not in grouped:
            grouped[elem] = []
        grouped[elem].append(p_pos)

    # Conquer: collect the weakest target from each element group
    priority_targets = []
    for elem, positions in grouped.items():
        weakest_pos = min(positions, key=lambda p: grid.tiles[p[0]][p[1]].card.hp)
        priority_targets.append(weakest_pos)

    # If we have priority targets, let greedy pick among them; otherwise all
    candidates = priority_targets if priority_targets else players
    return greedy_best_target(attacker_pos, candidates, grid)

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
    Skips heal attacks for CPU offense (heal is self-heal, not useful for attacking)
    """
    if not target_pos: return None
    
    best_attack = None
    max_score = -1
    
    dist = abs(attacker_pos[0] - target_pos[0]) + abs(attacker_pos[1] - target_pos[1])
    
    for atk in attacker_card.attacks:
        # Skip heal attacks when picking offensive attack
        is_heal = ("heal" in atk.name.lower()) or ("heal" in getattr(atk, 'animation', '').lower())
        if is_heal:
            continue
        if dist <= atk.attack_range:
            score = atk.dmg
            if atk.element == "fire": score += 2
            if score > max_score:
                max_score = score
                best_attack = atk
                
    return best_attack
