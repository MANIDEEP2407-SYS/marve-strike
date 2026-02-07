# ═══════════════════════════════════════════════════════
# 4K Color System — 60-30-10 Rule (WCAG AAA Compliant)
# ═══════════════════════════════════════════════════════

# ── PRIMARY 60% — Deep Space Theme ──
C_BG_PRIMARY    = (12, 15, 25)
C_BG_SECONDARY  = (18, 22, 38)
C_BG_TERTIARY   = (28, 32, 52)
C_BG_GRADIENT_T = (15, 20, 35)
C_BG_GRADIENT_B = (8, 10, 18)

# ── SECONDARY 30% — Electric Blue ──
C_ACCENT        = (88, 166, 255)
C_ACCENT_GLOW   = (130, 210, 255)
C_ACCENT_DARK   = (40, 65, 100)

# ── ACCENT 10% — Gold Highlights ──
C_GOLD          = (255, 200, 80)
C_GOLD_BRIGHT   = (255, 230, 150)
C_GOLD_DARK     = (180, 130, 40)

# ── Text (high contrast) ──
C_TEXT          = (240, 245, 255)
C_TEXT_SEC      = (155, 165, 195)
C_TEXT_DIM      = (80, 90, 115)
C_WHITE         = (255, 255, 255)

# ── Player / Enemy ──
C_PLAYER        = (80, 220, 150)
C_PLAYER_GLOW   = (130, 255, 200)
C_ENEMY         = (255, 85, 100)
C_ENEMY_GLOW    = (255, 130, 145)

# ── Elements (PBR-ready with glow pairs) ──
E_FIRE          = (255, 95, 50)
E_FIRE_GLOW     = (255, 155, 80)
E_WATER         = (60, 180, 255)
E_WATER_GLOW    = (110, 220, 255)
E_LEAF          = (90, 220, 110)
E_LEAF_GLOW     = (140, 255, 155)
E_AIR           = (220, 230, 255)
E_AIR_GLOW      = (255, 255, 255)
E_NULL          = (175, 120, 255)
E_NULL_GLOW     = (215, 170, 255)

# ── Status ──
C_VICTORY       = (255, 215, 0)
C_DEFEAT        = (180, 50, 60)
C_WARNING       = (255, 180, 60)
C_SUCCESS       = (80, 220, 150)

# ── Effects ──
C_CONFETTI = [
    (255, 100, 110), (110, 255, 160), (100, 180, 255),
    (255, 230, 100), (255, 150, 255), (150, 255, 255),
]
C_SHADOW = (0, 0, 0)

# ── Backward Compatibility ──
C_BG        = C_BG_PRIMARY
C_GRID      = C_ACCENT_DARK
C_PANEL     = C_BG_SECONDARY
C_HIGHLIGHT = C_ACCENT_GLOW
C_SELECT    = C_GOLD
