# CARD STRIKE: ELEMENTAL GUI

A strategic card battle game built with **Python + Pygame** where players draft cards, place units on a grid, and engage in tactical combat using elemental attacks.

---

## 🎮 Game Flow

| Phase | Description |
|---|---|
| **1. Stealing Phase** | Both player and CPU are dealt 5 cards from a pool of 20. Each side steals or retains until both have 3 cards. |
| **2. Placement Phase** | Player places 3 units on the grid; CPU auto-places its 3 units on empty tiles. |
| **3. Combat Phase** | Turn-based tactical combat — move units, attack enemies, heal allies. Press M for CPU turn. |
| **4. Victory/Defeat** | Game ends when one side loses all units. |

---

## 📂 Project Structure

```
├── main.py                  # Game loop, event handling, phase transitions
├── config.py                # Constants: grid size, tile size, window dimensions
├── colors.py                # Color palette (60-30-10 rule, element colors)
├── fonts.py                 # Font scale (FONT_MICRO → FONT_HERO)
├── card.py                  # Card and Tile dataclasses
├── attack.py                # Attack dataclass (name, dmg, element, range, animation)
├── cards.json               # 20 balanced cards + animation type definitions
├── game_grid.py             # Grid class, BFS reachability, adjacency graph
├── ui_draw.py               # Full UI rendering (grid, cards, bottom panel, help overlay)
├── animations.py            # 12 animation effect classes + AnimationManager
├── effects.py               # Persistent effects (flame tiles, regen, burn DOT)
├── logic_attack.py          # Attack resolution (damage, heal, special attacks)
├── stealing_phase.py        # Card draft/steal UI and logic
├── logic_cpu/
│   ├── advanced_cpu.py      # CPU turn controller (evaluate → execute best action)
│   ├── dc_combat.py         # Divide & Conquer: target selection, position, attack choice
│   ├── greedy_move.py       # Greedy movement toward ideal combat range
│   └── greedy_target_weakest.py  # Greedy target scoring (HP, distance, threat)
└── assets/                  # Card artwork (1.jpg – 20.jpeg)
```

---

## 🧠 Algorithms Used

### 1. BFS (Breadth-First Search) — Graph Traversal
**File:** `game_grid.py` → `bfs_reachable()`

Used for both **movement range** and **attack range** calculation. The grid is treated as an implicit unweighted graph where each tile is a node and 4-directional neighbors are edges.

```
Algorithm: BFS with depth limit
Input:     start position, max_depth, grid
Output:    set of all reachable (col, row) positions
Time:      O(V + E) where V = tiles within range, E = edges
Space:     O(V) for visited set + queue
```

- Movement range: `bfs_reachable(pos, card.move_range, grid)` → blue tiles
- Attack range: `bfs_reachable(pos, atk.attack_range, grid)` → red tiles
- CPU movement: BFS generates candidate positions for greedy evaluation

---

### 2. Greedy Algorithm — CPU Target Selection
**File:** `logic_cpu/greedy_target_weakest.py` → `greedy_best_target()`

The CPU uses a **greedy scoring function** to pick the best enemy to attack. Each candidate is scored on three weighted factors:

```
score = hp_factor × 10 + dist_factor × 5 + threat × 0.3

Where:
  hp_factor  = 1 - (card.hp / card.max_hp)     # prefer low-HP targets (kill potential)
  dist_factor = 1 / max(dist, 1)                # prefer closer targets
  threat      = max(attack.dmg for attacks)      # prefer high-damage threats
```

**Greedy choice:** Always pick the target with the highest score (locally optimal).

---

### 3. Greedy Algorithm — CPU Movement
**File:** `logic_cpu/greedy_move.py` → `greedy_nearest_move()`

After BFS finds reachable tiles, the CPU greedily selects the best position:

```
For each reachable empty tile (c, r):
    total_score = Σ |manhattan_dist(tile, player_i) - IDEAL_RANGE|
    edge_penalty = 2 if tile is on grid border
    score = total_score + edge_penalty

Pick tile with MINIMUM score (closest to ideal range from all players)
```

- **IDEAL_RANGE = 3** — the CPU tries to maintain optimal attack distance
- Edge penalty discourages corner-hugging

---

### 4. Divide and Conquer — CPU Combat Decision
**File:** `logic_cpu/dc_combat.py` → `select_attack_target()`

Target selection uses a **Divide & Conquer** approach:

```
DIVIDE:    Group all player units by element type
CONQUER:   Find the weakest (min HP) target in each element group
COMBINE:   Pass priority targets to greedy scoring for final pick
```

**File:** `logic_cpu/advanced_cpu.py` → `advanced_cpu_turn()`

The CPU evaluates all possible actions using D&C:

```
For each enemy unit:
    OPTION A: Evaluate ATTACK (D&C target → greedy attack pick → score)
    OPTION B: Evaluate MOVE (greedy position → score)

Execute the SINGLE action with the highest score.
Kill-blow bonus: +50 if attack would eliminate target.
```

---

### 5. Sorting — Card Draft, UI Display, Target Priority
**Files:** `stealing_phase.py`, `ui_draw.py`, `logic_cpu/dc_combat.py`

- **Stealing Phase:** `random.sample()` shuffles the card pool (Fisher-Yates internally)
- **Bottom Panel:** `player_cards.sort(key=lambda c: c.index)` — sorted display by slot index
- **D&C Conquer:** `min(positions, key=lambda p: grid.tiles[p[0]][p[1]].card.hp)` — selection sort to find weakest in each group
- **CPU Attack Selection:** Linear scan with max-tracking to find highest-damage attack in range (equivalent to finding max in unsorted list)

---

### 6. Manhattan Distance — Spatial Heuristic
**Files:** `logic_attack.py`, `greedy_move.py`, `greedy_target_weakest.py`, `dc_combat.py`

Used throughout for distance calculation on the grid:

```
dist = |x1 - x2| + |y1 - y2|
```

- Range checking: `if dist > atk.attack_range: return`
- Damage falloff: `base_dmg = atk.dmg - dist`
- CPU scoring: Distance factor in target selection and positioning

---

### 7. Linear Search — Entity Lookup
**Files:** `logic_attack.py`, `advanced_cpu.py`, `main.py`

Finding cards on the grid by owner/index:

```python
for c in range(GRID_COLS):
    for r in range(GRID_ROWS):
        card = grid.tiles[c][r].card
        if card and card.owner == "player" and card.index == player_idx:
            pc_pos = (c, r)
```

O(n×m) scan over all grid tiles — acceptable for 23×11 = 253 tiles.

---

### Algorithm Summary Table

| Algorithm | Type | File(s) | Purpose |
|-----------|------|---------|---------|
| **BFS** | Graph Traversal | `game_grid.py` | Movement + attack range |
| **Greedy (Target)** | Greedy | `greedy_target_weakest.py` | CPU picks best enemy to attack |
| **Greedy (Move)** | Greedy | `greedy_move.py` | CPU picks best tile to move to |
| **Divide & Conquer** | D&C | `dc_combat.py`, `advanced_cpu.py` | CPU combat decision tree |
| **Sorting** | Sort/Shuffle | `stealing_phase.py`, `ui_draw.py` | Card draft shuffle, display order |
| **Manhattan Distance** | Heuristic | Multiple files | Range checks, damage falloff, scoring |
| **Linear Search** | Search | `logic_attack.py`, `advanced_cpu.py` | Find cards on grid by owner/index |

---

## 🕹 Controls

| Key | Action |
|-----|--------|
| **Click** hero → **Click** tile | Move unit |
| **Hold 1/2/3** + **Q/W/E** | P1 attacks E1/E2/E3 |
| **Hold 1/2/3** + **A/S/D** | P2 attacks E1/E2/E3 |
| **Hold 1/2/3** + **Z/X/C** | P3 attacks E1/E2/E3 |
| **M** | Trigger CPU turn |
| **H** | Toggle help overlay |

---

## ⚙ Tech Stack

- **Python 3.13** + **Pygame 2.6.1**
- Window: 1472 × 964 px (23×11 grid + 260px bottom panel)
- 20 unique cards with 60 attacks across 5 elements
- 12 attack animation types (projectile, beam, slash, vine, whirlwind, heal, steam, glitch, splash, strike, trap, wave)