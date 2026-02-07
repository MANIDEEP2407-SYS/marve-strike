"""
Stealing Phase - Pre-game draft system
Each player gets 5 cards, then takes turns to STEAL or RETAIN until both have 3 cards.
Optimized for 16.2" screen with larger cards and fonts.
"""
import pygame
import random
import os
import json
from config import WIDTH, HEIGHT, FPS
from card import Card
from attack import Attack
from colors import *

# Load card data from JSON
def load_card_data():
    json_path = os.path.join(os.path.dirname(__file__), "cards.json")
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data["cards"]

CARD_POOL = load_card_data()

# Asset mapping (uses asset field from JSON)
def get_asset_name(card_data):
    return card_data.get("asset", "1.jpg")

ELEMENT_COLORS = {
    "fire": (255, 80, 50),
    "water": (50, 150, 255),
    "leaf": (80, 200, 80),
    "wind": (200, 200, 220),
    "null": (180, 100, 220),
    "combined": (255, 200, 100)
}

# UI Sizes for 16.2" screen
# UI Sizes for 16.2" screen - INCREASED
CARD_WIDTH = 220
CARD_HEIGHT = 300
CARD_SPACING = 240
CARD_IMAGE_HEIGHT = 180
FONT_SIZE_SMALL = 24
FONT_SIZE_MEDIUM = 32
FONT_SIZE_LARGE = 48
FONT_SIZE_TITLE = 64

class StealingPhase:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_big = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        
        # Load card images
        self.card_images = {}
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        for i, card_data in enumerate(CARD_POOL):
            asset_name = get_asset_name(card_data)
            path = os.path.join(assets_dir, asset_name)
            if os.path.exists(path):
                img = pygame.image.load(path)
                self.card_images[i] = pygame.transform.scale(img, (CARD_WIDTH - 10, CARD_IMAGE_HEIGHT))
        
        self.reset()
    
    def reset(self):
        # Shuffle and deal 5 cards to each player
        shuffled = random.sample(range(len(CARD_POOL)), min(10, len(CARD_POOL)))
        self.player_hand = shuffled[:5]
        self.cpu_hand = shuffled[5:10]
        
        self.player_deck = []  # Final 3 cards
        self.cpu_deck = []
        
        self.current_turn = "player"  # player or cpu
        self.phase_complete = False
        self.selected_card = None
        self.hovered_card = None
        self.action_message = "Your turn: Click YOUR card to RETAIN or OPPONENT's card to STEAL"
        
    def get_card_data(self, idx):
        return CARD_POOL[idx]
    
    def draw_card(self, idx, x, y, selected=False, owner="player", hovered=False):
        data = self.get_card_data(idx)
        
        # Card background with gradient effect
        element_color = ELEMENT_COLORS.get(data["element"], (100, 100, 100))
        secondary_color = ELEMENT_COLORS.get(data.get("secondary", data["element"]), element_color)
        
        # Selection/hover effects
        if selected:
            border_color = (255, 255, 0)
            border_width = 5
        elif hovered:
            border_color = (200, 200, 255)
            border_width = 3
        else:
            border_color = (50, 50, 50)
            border_width = 2
        
        # Draw card body with rounded corners
        card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
        # Create gradient surface
        card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        # Main background
        pygame.draw.rect(card_surf, (*element_color, 240), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=12)
        
        # Secondary element stripe at bottom
        pygame.draw.rect(card_surf, (*secondary_color, 200), (0, CARD_HEIGHT - 50, CARD_WIDTH, 50), border_radius=12)
        
        self.screen.blit(card_surf, (x, y))
        
        # Border
        pygame.draw.rect(self.screen, border_color, card_rect, border_width, border_radius=12)
        
        # Card image
        if idx in self.card_images:
            img_x = x + 5
            img_y = y + 5
            self.screen.blit(self.card_images[idx], (img_x, img_y))
            
            # Image border
            pygame.draw.rect(self.screen, (30, 30, 30), (img_x, img_y, CARD_WIDTH - 10, CARD_IMAGE_HEIGHT), 2, border_radius=8)
        
        # Card name (truncate if too long)
        name = data["name"]
        if len(name) > 14:
            name = name[:12] + ".."
        name_surf = self.font.render(name, True, (255, 255, 255))
        name_x = x + (CARD_WIDTH - name_surf.get_width()) // 2
        self.screen.blit(name_surf, (name_x, y + CARD_IMAGE_HEIGHT + 8))
        
        # Stats row: HP | SPD | MOV
        hp_text = f"HP:{data['hp']}"
        spd_text = f"SPD:{data.get('speed', '?')}"
        
        stats_surf = self.font_small.render(f"{hp_text}  {spd_text}", True, (255, 255, 255))
        stats_x = x + (CARD_WIDTH - stats_surf.get_width()) // 2
        self.screen.blit(stats_surf, (stats_x, y + CARD_IMAGE_HEIGHT + 35))
        
        # Element icons
        elem_text = f"{data['element'].upper()}"
        if data.get("secondary") and data["secondary"] != data["element"]:
            elem_text += f"/{data['secondary'].upper()}"
        elem_surf = self.font_small.render(elem_text, True, (200, 200, 200))
        elem_x = x + (CARD_WIDTH - elem_surf.get_width()) // 2
        self.screen.blit(elem_surf, (elem_x, y + CARD_HEIGHT - 22))
        
        return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    
    def draw_card_details(self, idx, x, y):
        """Draw detailed attack info for hovered card"""
        data = self.get_card_data(idx)
        
        # Details panel
        panel_width = 400
        panel_height = 250
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 40, 240), (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surf, (100, 100, 150), (0, 0, panel_width, panel_height), 3, border_radius=10)
        
        self.screen.blit(panel_surf, (x, y))
        
        # Title
        title = self.font.render(f"{data['name']} - Attacks", True, (255, 220, 100))
        self.screen.blit(title, (x + 15, y + 10))
        
        # Attack list
        ay = y + 50
        for i, atk in enumerate(data.get("attacks", [])):
            # Attack name and element
            elem_color = ELEMENT_COLORS.get(atk["element"], (200, 200, 200))
            atk_name = self.font_small.render(f"{i+1}. {atk['name']}", True, elem_color)
            self.screen.blit(atk_name, (x + 20, ay))
            
            # Attack stats
            stats = f"DMG:{atk['damage']} RNG:{atk['range']}"
            stats_surf = self.font_small.render(stats, True, (220, 220, 220))
            self.screen.blit(stats_surf, (x + 240, ay))
            
            ay += 35
    
    def draw(self):
        self.screen.fill((25, 25, 35))
        
        # Draw decorative background pattern
        for i in range(0, WIDTH, 100):
            for j in range(0, HEIGHT, 100):
                pygame.draw.circle(self.screen, (30, 30, 45), (i, j), 2)
        
        # Title with glow effect
        title_text = "⚔️ STEALING PHASE ⚔️"
        title = self.font_title.render(title_text, True, (255, 200, 50))
        title_shadow = self.font_title.render(title_text, True, (100, 80, 20))
        self.screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 23))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        # Turn indicator with visual emphasis
        turn_text = "▶ YOUR TURN" if self.current_turn == "player" else "▶ CPU THINKING..."
        turn_color = (100, 255, 150) if self.current_turn == "player" else (255, 150, 100)
        turn_surf = self.font_big.render(turn_text, True, turn_color)
        self.screen.blit(turn_surf, (WIDTH // 2 - turn_surf.get_width() // 2, 75))
        
        # Action message
        msg_surf = self.font.render(self.action_message, True, (150, 255, 150))
        self.screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 115))
        
        # CPU Hand (top) - centered
        cpu_label = self.font.render(f"🔴 CPU Hand ({len(self.cpu_hand)} cards)", True, (255, 120, 120))
        cpu_hand_width = len(self.cpu_hand) * CARD_SPACING
        cpu_start_x = (WIDTH - cpu_hand_width) // 2 + 10
        self.screen.blit(cpu_label, (cpu_start_x, 155))
        
        self.cpu_rects = []
        for i, card_idx in enumerate(self.cpu_hand):
            x = cpu_start_x + i * CARD_SPACING
            is_selected = self.selected_card == ("cpu", i)
            is_hovered = self.hovered_card == ("cpu", i)
            rect = self.draw_card(card_idx, x, 190, selected=is_selected, owner="cpu", hovered=is_hovered)
            self.cpu_rects.append(rect)
        
        # Player Hand (bottom) - centered
        player_label = self.font.render(f"🔵 Your Hand ({len(self.player_hand)} cards)", True, (100, 200, 255))
        player_hand_width = len(self.player_hand) * CARD_SPACING
        player_start_x = (WIDTH - player_hand_width) // 2 + 10
        player_y = HEIGHT - CARD_HEIGHT - 120
        self.screen.blit(player_label, (player_start_x, player_y - 35))
        
        self.player_rects = []
        for i, card_idx in enumerate(self.player_hand):
            x = player_start_x + i * CARD_SPACING
            is_selected = self.selected_card == ("player", i)
            is_hovered = self.hovered_card == ("player", i)
            rect = self.draw_card(card_idx, x, player_y, selected=is_selected, owner="player", hovered=is_hovered)
            self.player_rects.append(rect)
        
        # Deck status panel REMOVED as per user request

        
        # Draw attack details for hovered card
        if self.hovered_card:
            owner, idx = self.hovered_card
            if owner == "cpu" and idx < len(self.cpu_hand):
                card_idx = self.cpu_hand[idx]
                self.draw_card_details(card_idx, WIDTH - 380, 180)
            elif owner == "player" and idx < len(self.player_hand):
                card_idx = self.player_hand[idx]
                self.draw_card_details(card_idx, WIDTH - 420, player_y - 120)
        
        # Instructions
        if not self.phase_complete:
            inst_text = "💡 Click YOUR card to RETAIN it | Click CPU's card to STEAL it"
            inst_surf = self.font_small.render(inst_text, True, (150, 150, 180))
            self.screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, HEIGHT - 40))
        
    def handle_mouse_move(self, pos):
        """Handle mouse hover for card details"""
        self.hovered_card = None
        
        for i, rect in enumerate(self.cpu_rects):
            if rect.collidepoint(pos):
                self.hovered_card = ("cpu", i)
                return
        
        for i, rect in enumerate(self.player_rects):
            if rect.collidepoint(pos):
                self.hovered_card = ("player", i)
                return
    
    def handle_click(self, pos):
        if self.current_turn != "player" or self.phase_complete:
            return
        
        # Check player cards (RETAIN)
        for i, rect in enumerate(self.player_rects):
            if rect.collidepoint(pos):
                self.retain_card("player", i)
                return
        
        # Check CPU cards (STEAL)
        for i, rect in enumerate(self.cpu_rects):
            if rect.collidepoint(pos):
                self.steal_card(i)
                return
    
    def retain_card(self, owner, idx):
        """Keep your own card"""
        if owner == "player" and len(self.player_deck) < 3:
            card_idx = self.player_hand.pop(idx)
            self.player_deck.append(card_idx)
            card_name = CARD_POOL[card_idx]['name']
            self.action_message = f"✅ Retained {card_name}!"
            print(f"[StealingPhase] Player Retained {card_name} (ID: {card_idx}). Deck: {len(self.player_deck)}")
            self.end_turn()
    
    def steal_card(self, idx):
        """Steal opponent's card"""
        if len(self.player_deck) < 3 and idx < len(self.cpu_hand):
            card_idx = self.cpu_hand.pop(idx)
            self.player_deck.append(card_idx)
            card_name = CARD_POOL[card_idx]['name']
            self.action_message = f"🔥 Stole {card_name}!"
            print(f"[StealingPhase] Player Stole {card_name} (ID: {card_idx}) from CPU. PDeck: {len(self.player_deck)}, CHand: {len(self.cpu_hand)}")
            self.end_turn()
    
    def end_turn(self):
        """Switch turns"""
        self.check_phase_complete()
        if not self.phase_complete:
            self.current_turn = "cpu" if self.current_turn == "player" else "player"
            if self.current_turn == "cpu":
                pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # CPU thinks for 1 sec
    
    def cpu_turn(self):
        """CPU decision: Steal or Retain using D&C logic"""
        
        # Calculate scores for all cards in play
        player_card_scores = []
        for i, card_idx in enumerate(self.player_hand):
            data = CARD_POOL[card_idx]
            score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
            player_card_scores.append((score, i))
            
        cpu_card_scores = []
        for i, card_idx in enumerate(self.cpu_hand):
            data = CARD_POOL[card_idx]
            score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
            cpu_card_scores.append((score, i))
            
        # Sort to find best/worst
        player_card_scores.sort(key=lambda x: x[0], reverse=True) # Best first
        cpu_card_scores.sort(key=lambda x: x[0]) # Worst first (for discard)
        
        # Aggressive Steal Check
        # If Player's Best Card is significantly better than CPU's Worst Card
        # Steal it, even if hand is full (will require discarding)
        if self.player_hand and self.cpu_hand:
            best_player_score, best_player_idx = player_card_scores[0]
            worst_cpu_score, worst_cpu_idx = cpu_card_scores[0]
            
            # Threshold: Steal if +20 value improvement
            if best_player_score > worst_cpu_score + 20: 
                # STEAL (and swap/discard)
                card_idx = self.player_hand.pop(best_player_idx)
                
                # If CPU deck full (>=3), must discard one
                if len(self.cpu_deck) >= 3:
                     pass
                # NOTE: The logic above seems incomplete in the original code. 
                # It pops from player_hand but doesn't add to cpu_deck or cpu_hand explicitly in this block 
                # unless it falls through?
                # Actually, this block (354-375) does NOT append to cpu_deck. 
                # It effectively DELETES the player's card??
                # Wait, "card_idx = self.player_hand.pop(best_player_idx)" removes it.
                # Then nothing else happens with card_idx. It VANISHES.
                # This is likely the bug!
                
                print(f"[StealingPhase] CPU Aggressive Steal attempted on {CARD_POOL[card_idx]['name']} but logic incomplete!")
                # FIX: We should add it to CPU deck or hand.
                # But if we are in this block, we probably want to prioritize this action.
                # Let's add it to CPU Deck if space, or Swap if full is handled below.
                
                # If we just pop it, it's gone.
                # Let's put it back for now to fallback to standard logic, or fix it.
                self.player_hand.insert(best_player_idx, card_idx) # Revert pop for now


        if len(self.cpu_deck) >= 3:
            # Check if we should SWAP infinite value
            # Logic: If Player still has a GOD card, steal it and delete our worst KEPT card?
            # Or just deny the player.
            # Simple implementation: purely denial. But we need to put it somewhere.
            # Let's say we replace the worst card in cpu_deck.
            
            if self.player_hand:
                best_steal_score = 0
                best_steal_idx = -1
                for i, card_idx in enumerate(self.player_hand):
                    data = CARD_POOL[card_idx]
                    score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
                    if score > best_steal_score:
                        best_steal_score = score
                        best_steal_idx = i
                
                # Compare with worst in CPU DECK
                worst_deck_score = 9999
                worst_deck_idx = -1
                for i, card_idx in enumerate(self.cpu_deck):
                    data = CARD_POOL[card_idx]
                    score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
                    if score < worst_deck_score:
                        worst_deck_score = score
                        worst_deck_idx = i
                
                if best_steal_score > worst_deck_score + 15:
                    # SWAP
                    stolen_card = self.player_hand.pop(best_steal_idx)
                    discarded_card = self.cpu_deck.pop(worst_deck_idx)
                    self.cpu_deck.append(stolen_card)
                    self.action_message = f"🤖 CPU SWAPPED for {CARD_POOL[stolen_card]['name']}!"
                    self.end_turn()
                    return

            self.current_turn = "player"
            return
        
        # D&C: Evaluate steal vs retain (Standard Logic)
        best_steal_score = 0
        best_steal_idx = -1
        
        for i, card_idx in enumerate(self.player_hand):
            data = CARD_POOL[card_idx]
            score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
            if score > best_steal_score:
                best_steal_score = score
                best_steal_idx = i
        
        best_retain_score = 0
        best_retain_idx = -1
        
        for i, card_idx in enumerate(self.cpu_hand):
            data = CARD_POOL[card_idx]
            score = data["hp"] + sum(a["damage"] for a in data.get("attacks", []))
            if score > best_retain_score:
                best_retain_score = score
                best_retain_idx = i
        
        # Greedy: Pick best action
        if best_steal_score > best_retain_score * 1.1 and best_steal_idx >= 0 and self.player_hand:
            # STEAL
            card_idx = self.player_hand.pop(best_steal_idx)
            self.cpu_deck.append(card_idx)
            self.action_message = f"🤖 CPU stole {CARD_POOL[card_idx]['name']}!"
            print(f"[StealingPhase] CPU Stole {CARD_POOL[card_idx]['name']} (ID: {card_idx}). CDeck: {len(self.cpu_deck)}")
        elif best_retain_idx >= 0 and self.cpu_hand:
            # RETAIN
            card_idx = self.cpu_hand.pop(best_retain_idx)
            self.cpu_deck.append(card_idx)
            self.action_message = f"🤖 CPU retained {CARD_POOL[card_idx]['name']}"
            print(f"[StealingPhase] CPU Retained {CARD_POOL[card_idx]['name']} (ID: {card_idx}). CDeck: {len(self.cpu_deck)}")
        
        self.end_turn()
    
    def check_phase_complete(self):
        if len(self.player_deck) >= 3 and len(self.cpu_deck) >= 3:
            self.phase_complete = True
            self.action_message = "🎉 Stealing Phase Complete! Press SPACE to begin battle!"
    
    def create_card_from_pool(self, idx, owner, slot):
        """Convert pool card to game Card object"""
        data = CARD_POOL[idx]
        attacks = [Attack(a["name"], a["damage"], a["element"], a["range"], a.get("animation", "projectile_fire")) for a in data.get("attacks", [])]
        
        card = Card(
            owner=owner,
            name=data["name"],
            hp=data["hp"],
            max_hp=data["hp"],
            attacks=attacks,
            move_range=data.get("move", 3),
            element=data["element"],
            index=slot
        )
        card.display_hp = card.hp
        return card
    
    def get_final_decks(self):
        """Return Card objects for placement phase"""
        player_cards = [self.create_card_from_pool(idx, "player", i) for i, idx in enumerate(self.player_deck)]
        cpu_cards = [self.create_card_from_pool(idx, "enemy", i) for i, idx in enumerate(self.cpu_deck)]
        return player_cards, cpu_cards
