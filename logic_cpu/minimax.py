"""
Minimax AI Engine — Divide & Conquer Algorithm for CPU Decision Making

The Minimax algorithm is a classic Divide & Conquer (DAC) approach:
  DIVIDE:   Generate all possible moves (attack / move) for the current player
  CONQUER:  Recursively evaluate the resulting board states for each move
  COMBINE:  Pick the move that maximizes CPU score (or minimizes player score)

This module operates on lightweight state snapshots to avoid touching
the real game objects, animations, or global effects.
"""

import copy
from logic_attack import simulate_attack_damage, RARITY_MULT
from game_grid import bfs_reachable

# ═══════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════
MAX_DEPTH = 2          # Look-ahead depth (2 = CPU turn → Player response)
INF = 999999

# Rarity value weights for evaluation
RARITY_VALUE = {
    "normal": 1.0,
    "rare": 1.3,
    "epic": 1.6,
    "legendary": 2.0,
}


# ═══════════════════════════════════════
# LIGHTWEIGHT STATE SNAPSHOT
# ═══════════════════════════════════════
class UnitSnapshot:
    """Minimal card state for simulation — no Pygame objects."""
    __slots__ = ['owner', 'name', 'hp', 'max_hp', 'attacks', 'move_range',
                 'element', 'rarity', 'shield', 'pos']

    def __init__(self, card, pos):
        self.owner = card.owner
        self.name = card.name
        self.hp = card.hp
        self.max_hp = card.max_hp
        self.attacks = card.attacks          # Attack dataclass list (read-only)
        self.move_range = card.move_range
        self.element = card.element
        self.rarity = getattr(card, 'rarity', 'normal')
        self.shield = getattr(card, 'shield', 0)
        self.pos = pos                       # (col, row)

    def clone(self):
        """Fast shallow clone — attacks list is read-only so shared ref is safe."""
        c = UnitSnapshot.__new__(UnitSnapshot)
        c.owner = self.owner
        c.name = self.name
        c.hp = self.hp
        c.max_hp = self.max_hp
        c.attacks = self.attacks
        c.move_range = self.move_range
        c.element = self.element
        c.rarity = self.rarity
        c.shield = self.shield
        c.pos = self.pos
        return c


class BoardState:
    """Lightweight board snapshot for Minimax simulation."""

    def __init__(self, grid):
        self.cols = grid.cols
        self.rows = grid.rows
        self.units = []  # list of UnitSnapshot
        for c in range(grid.cols):
            for r in range(grid.rows):
                card = grid.tiles[c][r].card
                if card:
                    self.units.append(UnitSnapshot(card, (c, r)))

    def clone(self):
        """Deep-copy the board state (units only, no grid tiles)."""
        b = BoardState.__new__(BoardState)
        b.cols = self.cols
        b.rows = self.rows
        b.units = [u.clone() for u in self.units]
        return b

    def get_units(self, owner):
        return [u for u in self.units if u.owner == owner and u.hp > 0]

    def get_unit_at(self, pos):
        for u in self.units:
            if u.pos == pos and u.hp > 0:
                return u
        return None

    def remove_dead(self):
        self.units = [u for u in self.units if u.hp > 0]


# ═══════════════════════════════════════
# MOVE GENERATION (DIVIDE step)
# ═══════════════════════════════════════
def generate_moves(state, owner, grid):
    """
    DIVIDE: Generate all possible actions for `owner`.
    Each action is a dict: {'type': 'ATTACK'|'MOVE', ...}
    """
    moves = []
    my_units = state.get_units(owner)
    enemy_owner = "player" if owner == "enemy" else "enemy"
    enemies = state.get_units(enemy_owner)

    if not enemies:
        return moves

    for unit in my_units:
        uc, ur = unit.pos

        # --- Generate ATTACK moves ---
        for atk in unit.attacks:
            # Skip heal attacks for offensive evaluation
            is_heal = ("heal" in atk.name.lower()) or \
                      ("heal" in getattr(atk, 'animation', '').lower())
            if is_heal:
                continue

            for enemy in enemies:
                ec, er = enemy.pos
                dist = abs(uc - ec) + abs(ur - er)
                if dist <= atk.attack_range:
                    moves.append({
                        'type': 'ATTACK',
                        'unit_pos': unit.pos,
                        'target_pos': enemy.pos,
                        'attack': atk,
                        'dist': dist,
                    })

        # --- Generate MOVE moves ---
        # Use BFS on real grid for obstacle-aware reachability
        reachable = bfs_reachable(unit.pos, unit.move_range, grid)
        for new_pos in reachable:
            if new_pos == unit.pos:
                continue
            # Can't move to occupied tile
            if state.get_unit_at(new_pos) is not None:
                continue
            moves.append({
                'type': 'MOVE',
                'unit_pos': unit.pos,
                'new_pos': new_pos,
            })

    return moves


# ═══════════════════════════════════════
# APPLY MOVE (simulate on cloned state)
# ═══════════════════════════════════════
def apply_move(state, move):
    """Apply a move to a BoardState (mutates in place). Returns damage dealt."""
    if move['type'] == 'ATTACK':
        attacker = state.get_unit_at(move['unit_pos'])
        target = state.get_unit_at(move['target_pos'])
        if attacker and target:
            dmg = simulate_attack_damage(attacker, target, move['attack'], move['dist'])
            target.hp -= dmg
            if target.shield > 0:
                absorbed = min(target.shield, dmg)
                target.shield -= absorbed
            if target.hp <= 0:
                state.remove_dead()
            return dmg

    elif move['type'] == 'MOVE':
        unit = state.get_unit_at(move['unit_pos'])
        if unit:
            unit.pos = move['new_pos']

    return 0


# ═══════════════════════════════════════
# EVALUATION FUNCTION (COMBINE step)
# ═══════════════════════════════════════
def evaluate(state):
    """
    Evaluate board from CPU (enemy) perspective.
    Positive = good for CPU, Negative = good for player.

    Factors:
    1. Material: HP-weighted unit value (rarity matters)
    2. Kill advantage: difference in surviving units
    3. Positional: units closer to enemies can threaten
    """
    cpu_score = 0.0
    player_score = 0.0

    cpu_units = state.get_units("enemy")
    player_units = state.get_units("player")

    # Material score
    for u in cpu_units:
        value = RARITY_VALUE.get(u.rarity, 1.0)
        hp_ratio = u.hp / max(u.max_hp, 1)
        # Base value: max_hp * rarity factor, scaled by remaining HP
        cpu_score += (u.max_hp * value * 0.5) + (hp_ratio * value * 30)
        # Attack potential bonus
        best_dmg = max((a.dmg for a in u.attacks), default=0)
        cpu_score += best_dmg * value * 0.3

    for u in player_units:
        value = RARITY_VALUE.get(u.rarity, 1.0)
        hp_ratio = u.hp / max(u.max_hp, 1)
        player_score += (u.max_hp * value * 0.5) + (hp_ratio * value * 30)
        best_dmg = max((a.dmg for a in u.attacks), default=0)
        player_score += best_dmg * value * 0.3

    # Kill advantage bonus (huge swing for eliminating a unit)
    unit_diff = len(cpu_units) - len(player_units)
    kill_bonus = unit_diff * 50

    # Threat proximity: CPU units close to player units can attack
    threat_bonus = 0
    for cu in cpu_units:
        for pu in player_units:
            dist = abs(cu.pos[0] - pu.pos[0]) + abs(cu.pos[1] - pu.pos[1])
            best_range = max((a.attack_range for a in cu.attacks), default=3)
            if dist <= best_range:
                threat_bonus += 8  # In attack range — good for CPU
            elif dist <= best_range + cu.move_range:
                threat_bonus += 3  # Can reach next turn

    return (cpu_score - player_score) + kill_bonus + threat_bonus


# ═══════════════════════════════════════
# MINIMAX with ALPHA-BETA PRUNING
# ═══════════════════════════════════════
def minimax(state, depth, alpha, beta, is_maximizing, grid):
    """
    Recursive Divide & Conquer:
      - DIVIDE:   generate_moves() branches into all possible futures
      - CONQUER:  recursively evaluate each branch
      - COMBINE:  alpha-beta pruning selects the optimal path

    is_maximizing=True  → CPU turn (wants highest score)
    is_maximizing=False → Player turn (wants lowest score)
    """
    # Base case: leaf node or game over
    cpu_alive = len(state.get_units("enemy"))
    player_alive = len(state.get_units("player"))

    if depth == 0 or cpu_alive == 0 or player_alive == 0:
        return evaluate(state), None

    owner = "enemy" if is_maximizing else "player"
    moves = generate_moves(state, owner, grid)

    if not moves:
        return evaluate(state), None

    best_move = None

    if is_maximizing:
        max_eval = -INF
        for move in moves:
            child = state.clone()
            apply_move(child, move)
            eval_score, _ = minimax(child, depth - 1, alpha, beta, False, grid)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff (prune)
        return max_eval, best_move
    else:
        min_eval = INF
        for move in moves:
            child = state.clone()
            apply_move(child, move)
            eval_score, _ = minimax(child, depth - 1, alpha, beta, True, grid)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff (prune)
        return min_eval, best_move


# ═══════════════════════════════════════
# PUBLIC API — Called by advanced_cpu.py
# ═══════════════════════════════════════
def minimax_best_action(grid, depth=MAX_DEPTH):
    """
    Entry point: Snapshot the board, run Minimax DAC, return best action dict.
    Returns None if no valid moves exist.

    The returned action dict matches the format expected by advanced_cpu.py:
      {'type': 'ATTACK', 'unit_pos': (c,r), 'target_pos': (c,r), 'attack': Attack, 'dist': int}
      {'type': 'MOVE',   'unit_pos': (c,r), 'new_pos': (c,r)}
    """
    state = BoardState(grid)

    # Quick check: any CPU units alive?
    if not state.get_units("enemy"):
        return None

    score, best_move = minimax(state, depth, -INF, INF, True, grid)

    if best_move:
        print(f"[MINIMAX] Best action: {best_move['type']} | Score: {score:.1f}")
    else:
        print(f"[MINIMAX] No valid moves found.")

    return best_move
