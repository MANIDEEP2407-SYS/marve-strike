# 🎮 MARVEL STRIKE - 4K UI/UX REDESIGN SPECIFICATION
**Elite Senior Game UI/UX Design Document**
**Target: 4K Resolution - Professional 8px Grid System**

---

## 📐 DESIGN SYSTEM FOUNDATION

### 8px Grid System
```
Base Unit: 8px
- Padding SM: 16px (2 units)
- Padding MD: 24px (3 units)
- Padding LG: 32px (4 units)
- Padding XL: 48px (6 units)

Border Radius:
- SM: 8px (soft corners)
- MD: 16px (cards, buttons)
- LG: 24px (modals, panels)

Tile Size: 96px (12 × 8px units)
```

### Color Palette - 60-30-10 Rule (WCAG AAA)

#### PRIMARY (60%) - Deep Space
```python
C_BG_PRIMARY = (12, 15, 25)         # Rich Dark Navy
C_BG_SECONDARY = (18, 22, 35)       # Panel Background
C_BG_TERTIARY = (25, 30, 45)        # Hover State
```

#### SECONDARY (30%) - Electric Blue
```python
C_ACCENT_PRIMARY = (88, 166, 255)   # Professional Blue
C_ACCENT_GLOW = (120, 200, 255)     # Bright Glow
C_ACCENT_DARK = (45, 100, 180)      # Border Color
```

#### ACCENT (10%) - Gold Highlights
```python
C_GOLD = (255, 200, 80)             # Warm Gold
C_GOLD_BRIGHT = (255, 230, 150)     # Glow Effect
C_GOLD_DARK = (200, 150, 50)        # Dark Border
```

### Typography - 4K Optimized
```python
# Body (Sans-Serif)
FONT_MICRO = 16px    # Labels
FONT_MAIN = 24px     # Body text
FONT_BIG = 32px      # Headings
FONT_LARGE = 40px    # Large headings

# Display (Bold)
FONT_DMG = 48px      # Damage numbers
FONT_TITLE = 80px    # Titles
FONT_HERO = 96px     # Banner text
```

---

## 🎬 PAGE 1: MAIN MENU

### Breathtaking 4K Cinematic Entrance

#### Background (4 Layers)
1. **Animated Gradient**: (15,20,35) → (8,10,18) with subtle pan
2. **Floating Particles**: 50-80 dust motes, 2-4px, slow Perlin motion
3. **Light Rays**: 3-5 diagonal rays, rotating 0.1°/frame
4. **Vignette**: Radial gradient keeping UI crisp

#### Title Section
```
"⚔️ MARVEL STRIKE ⚔️"
- Font: FONT_HERO (96px)
- Color: C_GOLD_BRIGHT
- Effects: Drop shadow (6px), outer glow (12px), pulse 1.0→1.02

Subtitle: "Elemental Card Battle"
- Font: FONT_LARGE (40px)
- Color: C_TEXT_SECONDARY
- Letter spacing: 2px
```

#### START Button (PRIMARY FOCAL POINT)
```
Size: 320×80px
Background: Gold gradient with 3px C_GOLD_BRIGHT border
Shadow: 0 8px 24px C_GOLD @ 50%
Text: "START GAME" - FONT_XL (56px) Bold

Hover: Scale 1.05, glow 16px
Active: Scale 0.98
```

#### Secondary Actions
- "HOW TO PLAY" & "SETTINGS"
- FONT_BIG (32px), C_TEXT_SECONDARY
- Hover: C_ACCENT_GLOW with underline

---

## 🃏 PAGE 2: STEALING PHASE

### Immersive Card Selection Theater

#### Header
```
Title: "⚔️ STEALING PHASE ⚔️"
- FONT_TITLE (80px), C_GOLD_BRIGHT
- Glow: 16px blur

Progress Dots: 6 dots (3 per player)
- Filled: C_PLAYER / C_ENEMY
- Empty: C_TEXT_DISABLED
- Size: 16px, spacing 16px
- Pop animation on selection
```

#### Turn Indicator
```
"▶ YOUR TURN" / "▶ CPU THINKING..."
- FONT_LARGE (40px)
- Color: C_PLAYER_GLOW / C_ENEMY_GLOW
- Animated chevron pulse
- Panel: C_BG_SECONDARY, 24px radius
```

#### Enhanced Cards (280×380px)
```
Structure:
┌─────────────────────┐
│  Card Image         │ ← 280×240px PBR texture
│  (Asset photo)      │   2px border, 12px radius
├─────────────────────┤
│  Card Name          │ ← FONT_MEDIUM (28px)
│  ⚡ Element Icons   │
├─────────────────────┤
│  HP: 100  SPD: 5    │ ← FONT_SMALL (20px)
└─────────────────────┘

States:
- DEFAULT: Element color @ 90%, 2px border
- HOVER: 3px C_ACCENT_GLOW, scale 1.05, tooltip
- SELECTED: 4px C_GOLD_BRIGHT, glow 16px, scale 1.08
```

#### Attack Tooltip (480×320px)
```
Background: C_BG_SECONDARY @ 95%
Border: 2px C_ACCENT_PRIMARY
Radius: 16px
Shadow: 0 8px 32px

Content:
- Header: Card Name - Attacks
- 3 Attacks with icons:
  💥 DMG: X  📏 RNG: Y
- Fade + slide animation (200ms)
```

#### Feedback Messages
```
"✅ Retained [Card]!" / "🔥 Stole [Card]!"
- FONT_LARGE (40px)
- Panel: C_BG_TERTIARY, 16px radius
- Slide up + fade (2s)
```

---

## 🎮 PAGE 3: BATTLE GRID

### Transform "Not Nice" to "4K Premium"

#### Enhanced Background
```
- Gradient: C_BG_GRADIENT_TOP → BTM
- Animated noise: 2% opacity
- Grid lines: 1px C_GRID_LINE @ 25%
- Checkerboard tint: alternating tiles
```

#### Tile States (96×96px)
```
1. DEFAULT: 1px border
2. HOVER: Fill C_ACCENT_GLOW @ 15%, 2px border, glow 4px
3. MOVE RANGE: C_PLAYER @ 20%, pulsing, footstep icon
4. ATTACK RANGE: C_WARNING @ 15%, crosshair
5. SELECTED: C_GOLD @ 25%, 3px border, glow 8px, brackets
6. FLAME: Animated E_FIRE gradient, particles, flicker
```

#### Unit Visualization (72×72px in tile)
```
Layers:
1. Background Circle: 64px, element gradient, 3px border
2. Rotating Ring: 68px, 2px element glow, 0.5°/frame
3. Owner Fill: C_PLAYER/C_ENEMY @ 30%, pulse
4. Label: "P1"/"E1" - FONT_BIG (32px) Bold
5. HP Bar: 80×12px above tile
   - Gradient: C_SUCCESS → C_WARNING → C_DEFEAT
   - Text: FONT_SMALL (20px)
6. Status Icons: 24×24px, animated

Rarity:
- LEGENDARY: 4px C_GOLD border, 12px glow, sparkles
- EPIC: 3px E_NULL border, 8px glow, shimmer
- RARE: 2px C_ACCENT border, 6px glow
```

#### Combat Effects
```
Attack Trail: Bezier curve, element particles
Impact: Radial burst (20-30 particles)
Screen shake: 2-4px (100ms)

Damage Numbers:
- FONT_DMG (48px) Bold
- Pop: 0.5→1.2→1.0 scale, float -60px, 1.2s
- Critical: +30% scale, C_GOLD_BRIGHT

Heal: C_SUCCESS with ✨ sparkles
```

#### Bottom Panel (Full width × 240px)
```
3-Column Layout:
┌──────────────┬──────────────┬──────────────┐
│   Status     │ Instructions │  Attack Keys │
└──────────────┴──────────────┴──────────────┘

LEFT - Game Status:
- Turn: PLAYER/ENEMY (colored)
- Phase: Placement/Combat
- Elements: 🔥[1] 💧[2] 🍃[3] ⭐[4]

CENTER - Controls:
- Move: Click Hero → Tile
- Attack: Hold [1/2/3] + [Q-C]
- Enemy: Press [M]

RIGHT - Attack Keys:
- Hero 1: Q W E
- Hero 2: A S D  
- Hero 3: Z X C
- Keys: 32×32px rounded squares

Style:
- Background: C_BG_SECONDARY @ 95%
- Border top: 2px C_ACCENT_DARK
- Shadow: 0 -8px 32px
- Headers: FONT_BIG (32px) C_GOLD
- Body: FONT_MAIN (24px) C_TEXT_PRIMARY
```

---

## 🏆 PAGE 4: FINISH SCREEN

### Cinematic Conclusion

#### Shared: Blur background + overlay gradient

### VICTORY STATE

#### Background Effects
```
- Confetti: 200 particles, 4-8px, C_CONFETTI colors
- Light Beams: 5-7 golden rays, C_GOLD @ 30%, rotating
- Sparkles: 40-60 stars, 3-6px, twinkle
```

#### Content
```
Trophy Icon: 160×160px
- Position: Center, Y=400px
- Glow: 32px blur C_GOLD @ 80%
- Animation: Scale pulse + rotation

Title: "🏆 VICTORY! 🏆"
- FONT_HERO (96px) Bold
- Color: C_VICTORY
- Stroke: 3px C_GOLD_DARK
- Glow: 24px blur
- Entry: Elastic scale animation

Subtitle: "The Elements Bow to Your Command"
- FONT_LARGE (40px)
- C_TEXT_PRIMARY
```

#### Stats Panel (640×280px)
```
Background: C_BG_SECONDARY @ 90%
Border: 2px C_GOLD
Radius: 24px

Content:
📊 BATTLE STATISTICS
⚔️  Enemies Defeated: 3
💥  Total Damage: 420
⏱️  Time: 3:45
🎯  Accuracy: 87%
```

#### Buttons
```
Primary: "PLAY AGAIN"
- 320×72px, gold gradient
- FONT_LARGE (40px) Bold
- Hover: Scale 1.05

Secondary: "MAIN MENU"
- 280×64px, C_BG_TERTIARY
- FONT_BIG (32px)
```

### DEFEAT STATE

#### Background
```
- Falling ash particles: 100, dark
- Red vignette: C_DEFEAT @ 50%, pulsing
- Desaturation: 50%, contrast -20%
```

#### Content
```
Skull Icon: 160×160px, C_DEFEAT, shake

Title: "💀 DEFEAT 💀"
- FONT_HERO (96px) Bold
- C_DEFEAT color
- Fade + shake animation

Subtitle: "The Elements Have Overcome You"
- FONT_LARGE (40px)
- C_TEXT_SECONDARY

Encouragement Panel (640×200px):
"Don't give up! Learn from defeat."
- FONT_MEDIUM (28px)

Buttons:
- Primary: "TRY AGAIN" (blue accent)
- Secondary: "MAIN MENU"
```

---

## 🎨 EFFECTS STANDARDS

### Particles
```
Fire: E_FIRE→GLOW, 3-8px, float up
Water: E_WATER→GLOW, 2-6px, wave motion
Leaf: E_LEAF→GLOW, 4-7px, spinning fall
```

### Shadows & Glows
```
Shadows:
- Small: 0 2px 4px @ 30%
- Medium: 0 4px 12px @ 50%
- Large: 0 8px 24px @ 70%
- XL: 0 16px 48px @ 80%

Glows:
- Soft: 4px @ 30%
- Medium: 8px @ 50%
- Strong: 16px @ 70%
- Intense: 24px @ 90%
```

### Animations
```
Timing:
- Ease-out: Clicks
- Ease-in-out: Transitions
- Elastic: Celebrations
- Bounce: Feedback

Duration:
- Micro: 100-200ms
- Short: 300-500ms
- Medium: 800-1200ms
- Long: 2000ms+
```

---

## ✅ ACCESSIBILITY

- High Contrast Mode: +1px borders, +20% text contrast
- Large Text: 1.25× scale, 1.5× line height
- Color Blind: Pattern overlays + shapes
- Screen Reader: Alt text, state announcements
- Focus: 4px C_ACCENT_GLOW outline

---

## 🚀 IMPLEMENTATION PHASES

**Phase 1**: Core system (config, colors, fonts)
**Phase 2**: Main menu (background, title, button)
**Phase 3**: Stealing phase (cards, tooltips, feedback)
**Phase 4**: Battle grid (tiles, units, panel)
**Phase 5**: Finish screen (victory/defeat states)
**Phase 6**: Polish (optimization, accessibility)

---

## 📊 PERFORMANCE TARGETS

- 60 FPS at 4K (3840×2160)
- Frame time: <16.67ms
- Particle limit: 300 concurrent
- Memory: <500MB
- GPU: <40%

---

**This specification transforms Marvel Strike into a premium 4K gaming experience with professional UI/UX design, following industry standards for visual hierarchy, accessibility, and performance.**
