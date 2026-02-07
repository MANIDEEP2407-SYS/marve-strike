"""
D&C #2: Steal Target Evaluation
"""

def evaluate_card_value(card, strategy_window):
    """
    Evaluates a single card's worth for stealing.
    """
    if not card:
        return 0
    
    score = (card.hp / card.max_hp) * 50
    avg_dmg = sum(a.dmg for a in card.attacks) / len(card.attacks) if card.attacks else 0
    score += avg_dmg * 2
    
    return score

def get_best_steal_target(grid, player_positions, strategy_window):
    """
    D&C #2: Find best player card to steal.
    """
    best_score = -1
    best_pos = None

    for c, r in player_positions:
        card = grid.tiles[c][r].card
        if card:
            score = evaluate_card_value(card, strategy_window)
            if score > best_score:
                best_score = score
                best_pos = (c, r)
    
    return best_pos, best_score
