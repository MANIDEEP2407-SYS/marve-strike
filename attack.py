from dataclasses import dataclass

@dataclass
class Attack:
    name: str
    dmg: int
    element: str = "null"  # fire, water, leaf, air, null, combined
    attack_range: int = 3
    animation: str = "projectile_fire"  # Animation type from cards.json
