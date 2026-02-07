import random
from config import GRID_COLS, GRID_ROWS, FPS
from game_grid import cell_center
from effects import flame_tiles, regen_effects, burn_effects
from colors import E_FIRE, E_LEAF
from animations import anim_mgr

RARITY_MULT = {
    "normal": 1.0,
    "rare": 1.1,
    "epic": 1.25,
    "legendary": 1.5
}


def perform_attack_logic(ac, ar, tc, tr, atk, grid, dist=0):
    # ------------------------------
    # RANGE SAFETY CHECK
    # ------------------------------
    dist = abs(ac - tc) + abs(ar - tr)
    if dist > atk.attack_range:
        return

    attacker = grid.tiles[ac][ar].card
    target = grid.tiles[tc][tr].card
    if not attacker:
        return

    # ------------------------------
    # DAMAGE BASE CALCULATION
    # ------------------------------
    dmg_reduction = dist
    base_dmg = atk.dmg - dmg_reduction

    if target:
        MAX_HIT_DAMAGE = int(target.max_hp * 0.25)
        base_dmg = max(1, min(base_dmg, MAX_HIT_DAMAGE))

    # =====================================================
    # 1. Burning Trail (FIRE) — NO FRIENDLY DAMAGE
    # =====================================================
    if atk.name == "Burning Trail":
        dx = 1 if tc > ac else -1

        for i in range(1, 6):
            nc = ac + dx * i
            if grid.in_bounds(nc, ar):
                if not any(ft[0] == nc and ft[1] == ar for ft in flame_tiles):
                    flame_tiles.append([nc, ar, FPS * 3, attacker.owner])

        anim_mgr.add_floating_text("🔥 FIRE TRAIL", *cell_center(ac, ar), E_FIRE)

        # upfront hit only if opponent
        if target and target.owner != attacker.owner:
            dmg = max(1, int(base_dmg * 0.5))
            target.hp -= dmg
            target.flash_timer = 10
            anim_mgr.add_floating_text(f"-{dmg}", *cell_center(tc, tr), E_FIRE)

            if target.hp <= 0:
                grid.tiles[tc][tr].card = None
        return

    # =====================================================
    # 2. Nature’s Embrace (LEAF) — HEAL ONCE ONLY
    # =====================================================
    if atk.name == "Nature's Embrace":
        plus = [(tc,tr),(tc+1,tr),(tc-1,tr),(tc,tr+1),(tc,tr-1)]

        for (x, y) in plus:
            if grid.in_bounds(x,y) and grid.tiles[x][y].card:
                c = grid.tiles[x][y].card

                # 🟢 HEAL TEAM ONLY (ONCE)
                if c.owner == attacker.owner and not c.healed_once:
                    regen_effects.append([c, 5, FPS * 2, (x,y)])
                    c.healed_once = True
                    anim_mgr.add_floating_text("+HEAL", *cell_center(x,y), E_LEAF)

                # 🔴 DAMAGE ENEMY ONLY
                elif c.owner != attacker.owner:
                    burn_effects.append([c, 8, FPS * 2, (x,y)])
                    anim_mgr.add_floating_text("-THORN", *cell_center(x,y), E_FIRE)

        return

    # =====================================================
    # 3. Burning–Embrace Fusion — TEAM SAFE
    # =====================================================
    if atk.name == "Burning-Embrace Fusion":
        around = [
            (tc+1,tr),(tc-1,tr),(tc,tr+1),(tc,tr-1),
            (tc+1,tr+1),(tc-1,tr-1),(tc+1,tr-1),(tc-1,tr+1)
        ]

        for (x,y) in around:
            if grid.in_bounds(x,y) and grid.tiles[x][y].card:
                c = grid.tiles[x][y].card

                # 🟢 HEAL TEAM ONCE
                if c.owner == attacker.owner and not c.healed_once:
                    regen_effects.append([c, 5, FPS * 2, (x,y)])
                    c.healed_once = True
                    anim_mgr.add_floating_text("+FUSION HEAL", *cell_center(x,y), E_LEAF)

                # 🔴 DAMAGE ENEMY ONLY
                elif c.owner != attacker.owner:
                    burn_effects.append([c, 10, FPS * 2, (x,y)])
                    anim_mgr.add_floating_text("-FUSION FIRE", *cell_center(x,y), E_FIRE)

        return

    # =====================================================
    # 4. Normal Attack — NO FRIENDLY FIRE
    # =====================================================
    if target and target.owner != attacker.owner:
        base = atk.dmg + random.randint(-2, 2)
        mult = RARITY_MULT.get(attacker.rarity, 1.0)
        dmg = int(base * mult)

        if target.shield > 0:
            absorbed = min(target.shield, dmg)
            target.shield -= absorbed
            dmg -= absorbed
            anim_mgr.add_floating_text(f"-{absorbed}🛡", *cell_center(tc,tr))

        if dmg > 0:
            target.hp -= dmg
            anim_mgr.add_floating_text(f"-{dmg}", *cell_center(tc,tr))

        target.flash_timer = 8

        if target.hp <= 0:
            grid.tiles[tc][tr].card = None


def initiate_player_attack(player_idx, attack_idx, enemy_idx, grid):
    if anim_mgr.blocking:
        return None

    pc_pos = None
    ec_pos = None

    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            card = grid.tiles[c][r].card
            if card:
                if card.owner == "player" and card.index == player_idx:
                    pc_pos = (c,r)
                elif card.owner == "enemy" and card.index == enemy_idx:
                    ec_pos = (c,r)

    if not pc_pos or not ec_pos:
        return False

    attacker = grid.tiles[pc_pos[0]][pc_pos[1]].card
    atk = attacker.attacks[attack_idx]

    from game_grid import bfs_reachable
    reachable = bfs_reachable(pc_pos, atk.attack_range, grid)

    if ec_pos not in reachable:
        anim_mgr.add_floating_text(
            "OUT OF RANGE!",
            *cell_center(*pc_pos),
            (255,180,0)
        )
        return False

    # Get animation type from attack
    anim_type = getattr(atk, 'animation', None)
    if anim_type is None:
        # Fallback based on element
        anim_type = f"projectile_{atk.element}" if atk.element != "null" else "beam_null"

    anim_mgr.trigger_attack_anim(
        cell_center(*pc_pos),
        cell_center(*ec_pos),
        atk.element,
        lambda: perform_attack_logic(
            pc_pos[0], pc_pos[1],
            ec_pos[0], ec_pos[1],
            atk, grid
        ),
        anim_type=anim_type
    )

    return True
