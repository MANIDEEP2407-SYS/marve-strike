"""
D&C #3: Strategic Timing
"""

def analyze_turn_window(current_turn, max_turns=20):
    """
    Divide -> Remaining turns into windows (Early, Mid, Late)
    Conquer -> Evaluate benefit in each window
    Combine -> Pick optimal timing strategy
    """
    if current_turn <= 5:
        return "early"
    elif current_turn <= 15:
        return "mid"
    else:
        return "late"

def get_steal_value_modifier(window):
    """
    Returns a multiplier for stealing based on the game phase.
    """
    if window == "early":
        return 1.2
    elif window == "mid":
        return 1.0
    else:
        return 0.8
