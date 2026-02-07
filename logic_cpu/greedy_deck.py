"""
Greedy Deck Construction and Retain vs Steal Logic
"""

def calculate_deck_score(deck_cards):
    """
    Evaluates the total strength of a deck.
    """
    total_score = 0
    elements = set()
    for card in deck_cards:
        if not card: continue
        score = (card.hp / card.max_hp) * 50
        avg_dmg = sum(a.dmg for a in card.attacks) / len(card.attacks) if card.attacks else 0
        score += avg_dmg * 2
        elements.add(card.element)
        total_score += score
    
    # Diversity bonus
    total_score += len(elements) * 10
    return total_score

def decide_steal_vs_retain(current_deck_score, steal_target_score, timing_window):
    """
    Greedy #2 — Retain vs Steal Decision
    """
    modifier = 1.0
    if timing_window == "early":
        modifier = 1.2
    elif timing_window == "late":
        modifier = 0.8
        
    potential_gain = steal_target_score * modifier
    
    return potential_gain > 30
