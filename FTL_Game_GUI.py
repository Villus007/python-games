"""
FTL Lite GUI v2 — Pausable Real-Time Combat Roguelike
======================================================
Navigate 5 sectors, manage crew / power / systems,
fight in pausable real-time, and destroy the Rebel Flagship.

Built with tkinter — no external dependencies.
"""

import tkinter as tk
from tkinter import font as tkfont
import random, math, time

# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW / PALETTE
# ═══════════════════════════════════════════════════════════════════════════════

WIN_W, WIN_H = 1200, 800
PX = 4  # pixel-art scale

PAL = {
    "bg":          "#08081a",
    "panel":       "#111128",
    "panel_light": "#1a1a38",
    "border":      "#2a2a5a",
    "text":        "#d0d8e8",
    "dim":         "#5a6898",
    "bright":      "#ffffff",
    "highlight":   "#00ff88",
    "danger":      "#ff4455",
    "warning":     "#ffaa22",
    "info":        "#44aaff",
    "shield":      "#4488ff",
    "hull":        "#33dd66",
    "fuel":        "#ff9933",
    "missile_c":   "#ff5544",
    "scrap":       "#ffdd44",
    "btn":         "#1a1a40",
    "btn_hover":   "#2e2e66",
    "btn_border":  "#4444aa",
    "btn_text":    "#d0d8e8",
    "star":        "#ffffff",
    "b_enemy":     "#ff4455",
    "b_event":     "#ffaa22",
    "b_store":     "#44aaff",
    "b_empty":     "#556688",
    "b_exit":      "#00ff88",
    "b_visited":   "#2a2a44",
    "b_current":   "#ffffff",
    "p_ship":      "#44ddff",
    "e_ship":      "#ff6666",
    "charge_bg":   "#1a1a30",
    "charge_fg":   "#44ff88",
    "charge_miss": "#ff8844",
    "sys_ok":      "#33cc66",
    "sys_dmg":     "#ff6644",
    "sys_off":     "#333350",
    "power_on":    "#44bbff",
    "power_off":   "#222240",
    "pause_bg":    "#000000",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA — Species / Weapons / Ships
# ═══════════════════════════════════════════════════════════════════════════════

SPECIES = {
    "Human":  {"hp": 100, "combat": 10, "repair": 10, "desc": "Versatile"},
    "Engi":   {"hp":  80, "combat":  5, "repair": 20, "desc": "Repair expert"},
    "Mantis": {"hp": 100, "combat": 20, "repair":  5, "desc": "Fierce fighter"},
    "Rock":   {"hp": 150, "combat": 12, "repair":  8, "desc": "Very tough"},
    "Zoltan": {"hp":  70, "combat":  8, "repair": 12, "desc": "+1 system power"},
}

# charge_time is in seconds of real-time
WEAPONS = {
    "Burst Laser I":   {"dmg": 2, "shots": 1, "pierce": 1,  "missile": False, "cost": 40,  "power": 1, "charge": 8},
    "Burst Laser II":  {"dmg": 1, "shots": 3, "pierce": 1,  "missile": False, "cost": 80,  "power": 2, "charge": 11},
    "Heavy Laser":     {"dmg": 4, "shots": 1, "pierce": 2,  "missile": False, "cost": 65,  "power": 2, "charge": 10},
    "Artemis Missile": {"dmg": 3, "shots": 1, "pierce": 99, "missile": True,  "cost": 30,  "power": 1, "charge": 9},
    "Hermes Missile":  {"dmg": 4, "shots": 1, "pierce": 99, "missile": True,  "cost": 55,  "power": 2, "charge": 7},
    "Ion Blast":       {"dmg": 1, "shots": 1, "pierce": 3,  "missile": False, "cost": 50,  "power": 1, "charge": 7},
    "Pike Beam":       {"dmg": 2, "shots": 2, "pierce": 0,  "missile": False, "cost": 60,  "power": 2, "charge": 14},
    "Hull Laser":      {"dmg": 3, "shots": 1, "pierce": 2,  "missile": False, "cost": 70,  "power": 2, "charge": 10},
    "Flak I":          {"dmg": 1, "shots": 3, "pierce": 0,  "missile": False, "cost": 65,  "power": 2, "charge": 9},
}

_NAMES = [
    "Alex","Brin","Cael","Dara","Eris","Finn","Gael","Hana",
    "Iris","Jace","Kira","Lorn","Mira","Niko","Orin","Pax",
    "Quinn","Reva","Sven","Tova","Uma","Vex","Wren","Xyla","Yuri","Zara",
]

SECTOR_COUNT = 5
BEACONS_PER_SECTOR = 7

# ─── Systems list (shared between player and enemy) ──────────────────────────
SYSTEM_NAMES = ["shields", "weapons", "engines", "piloting", "oxygen"]
SYSTEM_LABELS = {"shields": "Shields", "weapons": "Weapons", "engines": "Engines",
                 "piloting": "Piloting", "oxygen": "O2 / Life Sup."}

# ═══════════════════════════════════════════════════════════════════════════════
#  PIXEL ART
# ═══════════════════════════════════════════════════════════════════════════════

SHIP_PLAYER = [
    "......CC......",
    ".....CCCC.....",
    ".....CCCC.....",
    "....CCCCCC....",
    "...CCCCCCCC...",
    "..CCCCCCCCCC..",
    ".CCCCCWWCCCCC.",
    ".CCCWWWWWCCCC.",
    "CCCCWWWWWWCCCC",
    "CCCCCCCCCCCCCC",
    "ECCCCCCCCCCCCE",
    "EECCCCCCCCCEE.",
    ".EECCCCCCCEE..",
    "..EEEEEEEEEE..",
    "...EE....EE...",
    "...EE....EE...",
]

SHIP_ENEMY = [
    "......RR......",
    ".....RRRR.....",
    "....RRRRRR....",
    "...RRRRRRRR...",
    "..RRRRRRRRRR..",
    ".RRRRRDDRRRRR.",
    "RRRRRDDDDRRRRR",
    "RRRRDDDDDDRRRR",
    "RRRRRDDDDRRRRR",
    ".RRRRRDDRRRRR.",
    "..RRRRRRRRRR..",
    "FFRRRRRRRRRRFF",
    "FFFRRRRRRRFFF.",
    "..FFFFFFFFFF..",
    "...FF....FF...",
]

SHIP_FLAGSHIP = [
    "........RRRRRR........",
    ".......RRRRRRRR.......",
    "......RRRRRRRRRR......",
    ".....RRRRRRRRRRRR.....",
    "....RRRRRRRRRRRRRR....",
    "...RRRRRRDDDDRRRRRR...",
    "..RRRRRRDDDDDDRRRRR..",
    ".RRRRRRDDDDDDDDRRRRRR.",
    "RRRRRRRDDDDDDDDRRRRRRR",
    "RRRRRRRDDDDDDDDRRRRRRR",
    ".RRRRRRDDDDDDDDRRRRRR.",
    "..RRRRRRDDDDDDRRRRR..",
    "...RRRRRRDDDDRRRRRR...",
    "FFFRRRRRRRRRRRRRRRRFFF",
    "FFFFFRRRRRRRRRRRFFFFF.",
    "..FFFFFFFFFFFFFFFFFF..",
    "....FFFF....FFFF......",
]

ART_COLORS = {
    'C': PAL["p_ship"], 'W': "#ffffff", 'E': "#33aaff",
    'R': PAL["e_ship"], 'D': "#aa2222", 'F': "#ff8833", '.': None,
}

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_pixel_art(canvas, art, x, y, scale=PX, tag="art"):
    for ri, row in enumerate(art):
        for ci, ch in enumerate(row):
            c = ART_COLORS.get(ch)
            if c:
                rx, ry = x + ci * scale, y + ri * scale
                canvas.create_rectangle(rx, ry, rx + scale, ry + scale,
                                        fill=c, outline="", tags=tag)

def draw_stars(canvas, count=140):
    w, h = int(canvas["width"]), int(canvas["height"])
    for _ in range(count):
        sx, sy = random.randint(0, w), random.randint(0, h)
        br = random.choice(["#ffffff", "#aaaacc", "#8888aa", "#666688"])
        sz = random.choice([1, 1, 1, 2])
        canvas.create_rectangle(sx, sy, sx + sz, sy + sz,
                                fill=br, outline="", tags="stars")

def make_crew(species=None):
    if species is None:
        species = random.choice(list(SPECIES.keys()))
    s = SPECIES[species]
    return {"name": random.choice(_NAMES), "species": species,
            "hp": s["hp"], "max_hp": s["hp"],
            "combat": s["combat"], "repair": s["repair"]}

def make_systems(shield_lv=1, weapon_lv=2, engine_lv=1, pilot_lv=1, oxy_lv=1):
    """Create a systems dict.  Each system: {level, power, max_power, hp, max_hp}"""
    def sys(level):
        return {"level": level, "power": level, "max_power": level,
                "hp": level * 2, "max_hp": level * 2}
    return {
        "shields":  sys(shield_lv),
        "weapons":  sys(weapon_lv),
        "engines":  sys(engine_lv),
        "piloting": sys(pilot_lv),
        "oxygen":   sys(oxy_lv),
    }

def create_ship():
    return {
        "name": "The Kestrel",
        "hull": 30, "max_hull": 30,
        "systems": make_systems(1, 2, 1, 1, 1),
        "max_reactor": 8, "reactor_used": 0,
        "weapons": ["Burst Laser I", "Artemis Missile"],
        "crew": [make_crew("Human"), make_crew("Human"), make_crew("Engi")],
        "fuel": 18, "missiles": 10, "scrap": 30,
        "crew_assignments": {},  # system_name -> crew member index
    }

def ship_evade(ship):
    eng = ship["systems"]["engines"]
    base = eng["power"] * 8
    pilot = ship["systems"]["piloting"]
    pilot_bonus = pilot["power"] * 5
    return min(base + pilot_bonus, 50)

def ship_shield_layers(ship):
    sh = ship["systems"]["shields"]
    return max(0, sh["power"] // 1)

def total_power_used(ship):
    total = 0
    for sn in SYSTEM_NAMES:
        total += ship["systems"][sn]["power"]
    return total

def make_enemy(sector):
    templates = [
        {"name": "Pirate Scout",     "hull": 8,  "sh": 0, "dmg": 2, "ev": 12, "wlv": 1, "elv": 1},
        {"name": "Rebel Fighter",    "hull": 12, "sh": 1, "dmg": 3, "ev": 10, "wlv": 2, "elv": 1},
        {"name": "Mantis Raider",    "hull": 10, "sh": 0, "dmg": 4, "ev": 18, "wlv": 2, "elv": 2},
        {"name": "Rock Cruiser",     "hull": 18, "sh": 2, "dmg": 2, "ev": 5,  "wlv": 2, "elv": 1},
        {"name": "Slug Interceptor", "hull": 10, "sh": 1, "dmg": 3, "ev": 22, "wlv": 2, "elv": 2},
        {"name": "Auto-Scout",       "hull": 8,  "sh": 1, "dmg": 2, "ev": 28, "wlv": 1, "elv": 3},
        {"name": "Engi Bomber",      "hull": 14, "sh": 1, "dmg": 3, "ev": 10, "wlv": 3, "elv": 1},
    ]
    t = random.choice(templates)
    sc = 1 + sector * 0.3
    hp = int(t["hull"] * sc)
    num_weapons = min(1 + sector // 2, 3)
    wpn_pool = [w for w in WEAPONS if not WEAPONS[w]["missile"]]
    enemy_weapons = random.sample(wpn_pool, min(num_weapons, len(wpn_pool)))
    return {
        "name": t["name"],
        "hull": hp, "max_hull": hp,
        "systems": make_systems(
            t["sh"] + sector // 2,
            t["wlv"] + sector // 2,
            t["elv"] + sector // 3,
            1 + sector // 3,
            1,
        ),
        "evade": t["ev"] + sector * 3,
        "weapons": enemy_weapons,
        "weapon_charge": {w: 0.0 for w in enemy_weapons},
        "scrap": random.randint(12, 22) + sector * 8,
        "fuel": random.randint(1, 3),
        "missiles": random.randint(0, 2),
        "is_flagship": False,
    }

def make_flagship(phase=1):
    hp = 30 + phase * 15
    weaps = {
        1: ["Burst Laser II", "Heavy Laser", "Artemis Missile"],
        2: ["Heavy Laser", "Flak I", "Hermes Missile"],
        3: ["Burst Laser II", "Hull Laser", "Pike Beam", "Hermes Missile"],
    }[phase]
    return {
        "name": f"REBEL FLAGSHIP (Phase {phase})",
        "hull": hp, "max_hull": hp,
        "systems": make_systems(2 + phase, 3 + phase, 2, 2, 1),
        "evade": 12 + phase * 5,
        "weapons": weaps,
        "weapon_charge": {w: 0.0 for w in weaps},
        "scrap": 0, "fuel": 0, "missiles": 0,
        "is_flagship": True, "phase": phase,
    }

def generate_sector(sector_num):
    beacons = []
    for i in range(BEACONS_PER_SECTOR):
        if i == BEACONS_PER_SECTOR - 1:
            btype = "exit"
        else:
            r = random.random()
            if r < 0.35:   btype = "enemy"
            elif r < 0.55: btype = "event"
            elif r < 0.70: btype = "store"
            elif r < 0.85: btype = "empty"
            else:          btype = "enemy"
        beacons.append({"type": btype, "visited": False, "index": i})
    beacons[0]["visited"] = True
    return beacons

# Events
def get_random_event():
    events = [
        ("A distress signal echoes from a nearby moon.",
         [("Investigate the signal", "distress_help"), ("Ignore and move on", "distress_ignore")]),
        ("An asteroid field blocks the direct route.",
         [("Fly through carefully", "asteroid_brave"), ("Take a detour (-1 fuel)", "asteroid_avoid")]),
        ("A derelict ship drifts silently among the stars.",
         [("Send a boarding party", "derelict_board"), ("Scan from a distance", "derelict_scan")]),
        ("A traveling merchant hails you, offering supplies.",
         [("Trade 15 scrap for 5 fuel + 3 missiles", "merchant_trade"), ("Decline", "merchant_decline")]),
        ("A swirling nebula hides something within.",
         [("Explore the nebula", "nebula_explore"), ("Avoid it", "nebula_skip")]),
        ("A strange illness sweeps through the ship!",
         [("Spend 10 scrap on medicine", "illness_treat"), ("Hope they recover", "illness_ignore")]),
        ("An allied Federation ship offers to trade crew.",
         [("Accept a new crew member (random)", "fed_crew"), ("Decline politely", "fed_decline")]),
        ("You detect a hidden weapons cache on a small moon.",
         [("Land and search (risky)", "cache_land"), ("Too risky, move on", "cache_skip")]),
    ]
    return random.choice(events)

def resolve_event(key, ship):
    if key == "distress_help":
        if random.random() < 0.6:
            sp = random.choice(list(SPECIES.keys()))
            ship["crew"].append(make_crew(sp))
            return (f"Rescued a {sp} crew member! They join your ship.", "highlight")
        d = random.randint(1, 3); ship["hull"] -= d
        return (f"It was a trap! Hull takes {d} damage.", "danger")
    elif key == "distress_ignore":
        return ("You fly past. Nothing happens.", "dim")
    elif key == "asteroid_brave":
        if random.random() < 0.5:
            s = random.randint(10, 25); ship["scrap"] += s
            return (f"Navigated safely! Salvaged {s} scrap.", "highlight")
        d = random.randint(2, 5); ship["hull"] -= d
        return (f"Asteroids batter your hull for {d} damage!", "danger")
    elif key == "asteroid_avoid":
        ship["fuel"] -= 1
        return ("Detour costs 1 extra fuel.", "warning")
    elif key == "derelict_board":
        r = random.random()
        if r < 0.4:
            s = random.randint(15, 35); ship["scrap"] += s
            return (f"Found {s} scrap aboard the wreck!", "highlight")
        elif r < 0.7:
            wn = random.choice(list(WEAPONS.keys()))
            ship["weapons"].append(wn)
            return (f"Found a {wn} in the wreckage!", "highlight")
        d = random.randint(2, 4); ship["hull"] -= d
        return (f"Booby trap! {d} hull damage.", "danger")
    elif key == "derelict_scan":
        s = random.randint(5, 12); ship["scrap"] += s
        return (f"Scans reveal minor salvage: {s} scrap.", "dim")
    elif key == "merchant_trade":
        if ship["scrap"] >= 15:
            ship["scrap"] -= 15; ship["fuel"] += 5; ship["missiles"] += 3
            return ("Traded 15 scrap for 5 fuel + 3 missiles.", "highlight")
        return ("Not enough scrap! (need 15)", "danger")
    elif key == "merchant_decline":
        return ("You decline and move on.", "dim")
    elif key == "nebula_explore":
        if random.random() < 0.5:
            s = random.randint(8, 20); ship["scrap"] += s
            return (f"Found {s} scrap hidden in the nebula!", "highlight")
        return ("The nebula is empty.", "dim")
    elif key == "nebula_skip":
        return ("You steer clear.", "dim")
    elif key == "illness_treat":
        if ship["scrap"] >= 10:
            ship["scrap"] -= 10
            return ("Medicine purchased. Crew recovers!", "highlight")
        if ship["crew"]:
            lost = ship["crew"].pop()
            return (f"No scrap! {lost['name']} the {lost['species']} dies.", "danger")
        return ("No scrap and no crew left...", "danger")
    elif key == "illness_ignore":
        if ship["crew"] and random.random() < 0.4:
            lost = ship["crew"].pop()
            return (f"{lost['name']} the {lost['species']} couldn't survive.", "danger")
        return ("The crew toughs it out.", "dim")
    elif key == "fed_crew":
        sp = random.choice(list(SPECIES.keys()))
        ship["crew"].append(make_crew(sp))
        return (f"A {sp} crew member joins your ship!", "highlight")
    elif key == "fed_decline":
        return ("You respectfully decline.", "dim")
    elif key == "cache_land":
        if random.random() < 0.55:
            wn = random.choice(list(WEAPONS.keys()))
            ship["weapons"].append(wn)
            return (f"Found a {wn}!", "highlight")
        d = random.randint(2, 5); ship["hull"] -= d
        return (f"Cave-in! {d} hull damage.", "danger")
    elif key == "cache_skip":
        return ("You leave it alone.", "dim")
    return ("Nothing happens.", "dim")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class FTLApp:
    def __init__(self, root):
        self.root = root
        root.title("FTL Lite — Real-Time Combat Roguelike")
        root.geometry(f"{WIN_W}x{WIN_H}")
        root.resizable(False, False)
        root.configure(bg=PAL["bg"])

        self.canvas = tk.Canvas(root, width=WIN_W, height=WIN_H,
                                bg=PAL["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Fonts
        self.F_TITLE  = ("Consolas", 28, "bold")
        self.F_BIG    = ("Consolas", 18, "bold")
        self.F_MED    = ("Consolas", 13, "bold")
        self.F_BODY   = ("Consolas", 11)
        self.F_SMALL  = ("Consolas", 9)
        self.F_BTN    = ("Consolas", 11, "bold")
        self.F_TINY   = ("Consolas", 8)

        # Game state
        self.ship = None
        self.sector_num = 0
        self.beacons = []
        self.current_beacon = 0
        self.enemy = None
        self.flagship_phase = 0

        # Combat real-time state
        self.combat_running = False
        self.combat_paused = False
        self.combat_log = []
        self.player_weapon_charge = {}    # weapon_name -> float (0..1)
        self.combat_tick_id = None
        self.last_tick_time = 0
        self.target_system = "shields"    # which enemy system player is targeting
        self.combat_over = False
        self.shield_regen_timer = 0.0

        # Button tracking (for proper hover)
        self._btn_counter = 0

        self.show_title()

    # ──────────────────────────────────────────────────────────────────────────
    #  DRAWING UTILITIES
    # ──────────────────────────────────────────────────────────────────────────

    def clear(self):
        if self.combat_tick_id:
            self.root.after_cancel(self.combat_tick_id)
            self.combat_tick_id = None
        self.combat_running = False
        self.canvas.delete("all")
        draw_stars(self.canvas, 150)

    def panel(self, x, y, w, h, tag="p"):
        self.canvas.create_rectangle(x, y, x + w, y + h,
            fill=PAL["panel"], outline=PAL["border"], width=2, tags=tag)

    def btn(self, x, y, w, h, text, cmd, color=None, tag="btn"):
        """Draw a button with SEPARATE rect/text tags so hover works."""
        self._btn_counter += 1
        bg = color or PAL["btn"]
        rect_tag = f"btnR{self._btn_counter}"
        hit_tag  = f"btnH{self._btn_counter}"  # invisible hit-area on top

        self.canvas.create_rectangle(x, y, x + w, y + h,
            fill=bg, outline=PAL["btn_border"], width=2, tags=(tag, rect_tag))
        self.canvas.create_text(x + w // 2, y + h // 2, text=text,
            fill=PAL["btn_text"], font=self.F_BTN, tags=tag, width=w - 10)
        # Invisible hit rect on top (captures mouse)
        self.canvas.create_rectangle(x, y, x + w, y + h,
            fill="", outline="", tags=(tag, hit_tag))

        def enter(e):
            self.canvas.itemconfig(rect_tag, fill=PAL["btn_hover"])
        def leave(e):
            self.canvas.itemconfig(rect_tag, fill=bg)
        def click(e):
            cmd()
        self.canvas.tag_bind(hit_tag, "<Enter>", enter)
        self.canvas.tag_bind(hit_tag, "<Leave>", leave)
        self.canvas.tag_bind(hit_tag, "<Button-1>", click)

    def bar(self, x, y, w, h, cur, mx, fg, bg="#1a1a30", tag="bar", outline=True):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=bg, outline="", tags=tag)
        if mx > 0:
            fw = max(0, int(w * min(cur, mx) / mx))
            if fw > 0:
                self.canvas.create_rectangle(x, y, x + fw, y + h,
                    fill=fg, outline="", tags=tag)
        if outline:
            self.canvas.create_rectangle(x, y, x + w, y + h,
                fill="", outline=PAL["border"], width=1, tags=tag)

    def txt(self, x, y, text, color=None, font=None, anchor="nw", tag="t", width=0):
        kw = {}
        if width: kw["width"] = width
        self.canvas.create_text(x, y, text=text,
            fill=color or PAL["text"], font=font or self.F_BODY,
            anchor=anchor, tags=tag, **kw)

    # ── Top resource bar ──
    def draw_top_bar(self):
        if not self.ship:
            return
        s = self.ship
        self.panel(0, 0, WIN_W, 48, "top")
        self.txt(15, 24, f"{s['name']}", PAL["text"], self.F_MED, "w", "top")
        # Hull
        self.txt(210, 12, "HULL", PAL["dim"], self.F_TINY, "nw", "top")
        self.bar(250, 10, 110, 12, s["hull"], s["max_hull"], PAL["hull"], tag="top")
        self.txt(365, 12, f"{s['hull']}/{s['max_hull']}", PAL["text"], self.F_TINY, "nw", "top")
        # Shields
        sl = ship_shield_layers(s)
        self.txt(420, 12, f"Shields: {sl}", PAL["shield"], self.F_SMALL, "nw", "top")
        # Engines / evade
        self.txt(520, 12, f"Evade: {ship_evade(s)}%", PAL["dim"], self.F_SMALL, "nw", "top")
        # Resources
        self.txt(210, 30, f"Fuel: {s['fuel']}", PAL["fuel"], self.F_SMALL, "nw", "top")
        self.txt(310, 30, f"Missiles: {s['missiles']}", PAL["missile_c"], self.F_SMALL, "nw", "top")
        self.txt(440, 30, f"Scrap: {s['scrap']}", PAL["scrap"], self.F_SMALL, "nw", "top")
        self.txt(560, 30, f"Crew: {len(s['crew'])}", PAL["text"], self.F_SMALL, "nw", "top")
        self.txt(WIN_W - 15, 24, f"Sector {self.sector_num + 1}/{SECTOR_COUNT}",
                 PAL["info"], self.F_MED, "e", "top")

    # ══════════════════════════════════════════════════════════════════════════
    #  TITLE SCREEN
    # ══════════════════════════════════════════════════════════════════════════

    def show_title(self):
        self.clear()
        cx = WIN_W // 2
        self.canvas.create_text(cx, 90, text="F  T  L", fill=PAL["info"],
                                font=("Consolas", 64, "bold"))
        self.canvas.create_text(cx, 142, text="L   I   T   E", fill=PAL["highlight"],
                                font=("Consolas", 20, "bold"))
        self.canvas.create_text(cx, 178,
            text="A Pausable Real-Time Combat Roguelike",
            fill=PAL["dim"], font=self.F_BODY)
        aw = len(SHIP_PLAYER[0]) * PX * 2
        draw_pixel_art(self.canvas, SHIP_PLAYER, cx - aw // 2, 220, PX * 2)
        instructions = (
            "• Navigate 5 sectors — fight enemies, visit stores, encounter events\n"
            "• Real-time combat: weapons charge and fire — press SPACE to pause & give orders\n"
            "• Allocate reactor power between Shields, Weapons, Engines, Piloting, O2\n"
            "• Target enemy systems to disable their shields, weapons, or engines\n"
            "• Upgrade your ship at stores & defeat the Rebel Flagship to win!"
        )
        self.canvas.create_text(cx, 430, text=instructions,
            fill=PAL["text"], font=self.F_BODY, justify="center", width=700)
        self.btn(cx - 120, 540, 240, 55, "START  GAME", self.start_game, "#1a4430")
        self.canvas.create_text(cx, 660,
            text="Ship: The Kestrel  •  Crew: 2 Humans + 1 Engi\nWeapons: Burst Laser I, Artemis Missile",
            fill=PAL["dim"], font=self.F_SMALL, justify="center")
        self.canvas.create_text(cx, 740, text="v2.0  —  Python + tkinter",
            fill="#333355", font=self.F_TINY)

    def start_game(self):
        self.ship = create_ship()
        self.sector_num = 0
        self.flagship_phase = 0
        self.start_sector()

    # ══════════════════════════════════════════════════════════════════════════
    #  SECTOR MAP
    # ══════════════════════════════════════════════════════════════════════════

    def start_sector(self):
        self.beacons = generate_sector(self.sector_num)
        self.current_beacon = 0
        self.show_sector_map()

    def show_sector_map(self):
        self.clear()
        self.draw_top_bar()
        cx = WIN_W // 2
        s = self.ship

        # Check loss
        if s["hull"] <= 0 or not s["crew"] or s["fuel"] <= 0:
            reason = "Hull destroyed!" if s["hull"] <= 0 else \
                     "All crew lost!" if not s["crew"] else "Out of fuel!"
            self.root.after(300, lambda: self.show_game_over(False, reason))
            return

        self.txt(cx, 70, f"— Sector {self.sector_num + 1} —", PAL["text"], self.F_BIG, "center")

        # Rebel fleet warning
        visited_count = sum(1 for b in self.beacons if b["visited"])
        if visited_count >= BEACONS_PER_SECTOR - 1:
            self.txt(cx, 95, "⚠  The rebel fleet is closing in!  ⚠",
                     PAL["danger"], self.F_BODY, "center")

        # ── Beacon map ──
        n = len(self.beacons)
        mx = 100; spacing = (WIN_W - 2 * mx) / max(n - 1, 1)
        by_base = 200
        offsets = [0, -25, 18, -12, 22, -8, 0]
        bpos = [(mx + i * spacing, by_base + offsets[i % len(offsets)]) for i in range(n)]

        # Lines
        for i in range(n - 1):
            self.canvas.create_line(*bpos[i], *bpos[i + 1],
                fill=PAL["border"], width=2, dash=(6, 4))

        # Beacons
        bcolors = {"enemy": PAL["b_enemy"], "event": PAL["b_event"],
                    "store": PAL["b_store"], "empty": PAL["b_empty"], "exit": PAL["b_exit"]}
        bicons = {"enemy": "⚔", "event": "?", "store": "$", "empty": "·", "exit": "►"}
        for i, b in enumerate(self.beacons):
            bx, b_y = bpos[i]
            r = 22
            if i == self.current_beacon:
                self.canvas.create_oval(bx-r-4, b_y-r-4, bx+r+4, b_y+r+4,
                    fill="", outline=PAL["b_current"], width=3)
                ic, lbl_c = "☆", PAL["b_current"]
                col = PAL["panel_light"]
            elif b["visited"]:
                ic, lbl_c = "✓", PAL["dim"]
                col = PAL["b_visited"]
            else:
                ic = bicons.get(b["type"], "?")
                col = bcolors.get(b["type"], PAL["b_empty"])
                lbl_c = PAL["dim"]
            self.canvas.create_oval(bx-r, b_y-r, bx+r, b_y+r,
                fill=col, outline=PAL["border"], width=2)
            self.canvas.create_text(bx, b_y, text=ic,
                fill=PAL["text"], font=("Consolas", 14, "bold"))
            lbl = "YOU" if i == self.current_beacon else ("EXIT" if b["type"] == "exit" else f"B{i+1}")
            self.canvas.create_text(bx, b_y + r + 14, text=lbl,
                fill=lbl_c, font=self.F_SMALL)

        # ── Crew panel ──
        self.panel(25, 290, 520, 180)
        self.txt(35, 300, "CREW", PAL["info"], self.F_MED)
        for ci, crew in enumerate(s["crew"][:7]):
            cy = 325 + ci * 20
            hp_pct = crew["hp"] / crew["max_hp"]
            hc = PAL["highlight"] if hp_pct > 0.5 else (PAL["warning"] if hp_pct > 0.25 else PAL["danger"])
            self.txt(45, cy, f"{crew['name']} ({crew['species']})", PAL["text"], self.F_SMALL)
            self.bar(220, cy, 70, 10, crew["hp"], crew["max_hp"], hc)
            self.txt(295, cy, f"{crew['hp']}/{crew['max_hp']} HP  C:{crew['combat']} R:{crew['repair']}",
                     PAL["dim"], self.F_TINY)

        # ── Systems panel ──
        self.panel(560, 290, 300, 180)
        self.txt(570, 300, "SYSTEMS", PAL["info"], self.F_MED)
        for si, sn in enumerate(SYSTEM_NAMES):
            sy = 325 + si * 28
            sys = s["systems"][sn]
            label = SYSTEM_LABELS[sn]
            # Power pips
            for pi in range(sys["max_power"]):
                px = 660 + pi * 16
                col = PAL["power_on"] if pi < sys["power"] else PAL["power_off"]
                self.canvas.create_rectangle(px, sy, px + 12, sy + 14,
                    fill=col, outline=PAL["border"])
            # HP bar
            hc = PAL["sys_ok"] if sys["hp"] >= sys["max_hp"] else PAL["sys_dmg"]
            self.bar(760, sy, 60, 14, sys["hp"], sys["max_hp"], hc)
            self.txt(570, sy, label, PAL["text"], self.F_SMALL)
            self.txt(825, sy, f"{sys['hp']}/{sys['max_hp']}", PAL["dim"], self.F_TINY)

        # ── Weapons panel ──
        self.panel(875, 290, 300, 180)
        self.txt(885, 300, "WEAPONS", PAL["info"], self.F_MED)
        for wi, wname in enumerate(s["weapons"][:6]):
            wy = 325 + wi * 22
            w = WEAPONS[wname]
            mf = " [M]" if w["missile"] else ""
            self.txt(895, wy,
                f"• {wname} d:{w['dmg']}x{w['shots']} p:{w['pierce']}{mf}",
                PAL["text"], self.F_SMALL)

        # ── Jump buttons ──
        reachable = []
        for i in range(max(0, self.current_beacon), min(n, self.current_beacon + 3)):
            if i != self.current_beacon:
                reachable.append(i)
        if self.current_beacon + 1 < n and (self.current_beacon + 1) not in reachable:
            reachable.append(self.current_beacon + 1)
        reachable = sorted(set(reachable))

        self.txt(cx, 500, "Select a beacon to jump to:", PAL["text"], self.F_BODY, "center")
        bw = 170
        total = len(reachable) * (bw + 12) - 12
        sx = cx - total // 2
        for ji, idx in enumerate(reachable):
            b = self.beacons[idx]
            bx = sx + ji * (bw + 12)
            label = "► EXIT" if b["type"] == "exit" else f"Beacon {idx + 1}"
            if b["visited"]: label += " (vis)"
            col = "#1a3322" if b["type"] == "exit" else PAL["btn"]
            def jump_cmd(i=idx): self.jump_to(i)
            self.btn(bx, 520, bw, 40, label, jump_cmd, col)

        # ── Ship management button ──
        self.btn(25, 500, 200, 40, "⚙  Ship Management", self.show_ship_management, "#1a2244")

    # ──────────────────────────────────────────────────────────────────────────
    #  SHIP MANAGEMENT SCREEN
    # ──────────────────────────────────────────────────────────────────────────

    def show_ship_management(self):
        self.clear()
        self.draw_top_bar()
        s = self.ship
        cx = WIN_W // 2

        self.txt(cx, 70, "— Ship Management —", PAL["text"], self.F_BIG, "center")

        # ── Power allocation ──
        self.panel(30, 100, 540, 280)
        self.txt(40, 110, "REACTOR POWER ALLOCATION", PAL["info"], self.F_MED)
        used = total_power_used(s)
        self.txt(40, 135, f"Reactor: {used}/{s['max_reactor']} power used",
                 PAL["text"], self.F_BODY)

        for si, sn in enumerate(SYSTEM_NAMES):
            sy = 170 + si * 45
            sys = s["systems"][sn]
            label = SYSTEM_LABELS[sn]
            self.txt(50, sy + 5, label, PAL["text"], self.F_BODY)

            # Power pips
            for pi in range(sys["max_power"]):
                px = 200 + pi * 22
                col = PAL["power_on"] if pi < sys["power"] else PAL["power_off"]
                self.canvas.create_rectangle(px, sy, px + 18, sy + 20,
                    fill=col, outline=PAL["border"], width=1)

            # +/- buttons
            def add_power(name=sn):
                ss = s["systems"][name]
                if ss["power"] < ss["max_power"] and total_power_used(s) < s["max_reactor"]:
                    # Check system HP — damaged systems have reduced max power
                    effective_max = max(0, ss["level"] - max(0, ss["max_hp"] - ss["hp"]))
                    if ss["power"] < effective_max:
                        ss["power"] += 1
                self.show_ship_management()
            def sub_power(name=sn):
                ss = s["systems"][name]
                if ss["power"] > 0:
                    ss["power"] -= 1
                self.show_ship_management()

            self.btn(200 + sys["max_power"] * 22 + 10, sy - 2, 30, 24, "+", add_power, "#224422")
            self.btn(200 + sys["max_power"] * 22 + 45, sy - 2, 30, 24, "-", sub_power, "#442222")

            # System HP
            hc = PAL["sys_ok"] if sys["hp"] >= sys["max_hp"] else PAL["sys_dmg"]
            self.bar(420, sy, 80, 18, sys["hp"], sys["max_hp"], hc)
            self.txt(505, sy + 3, f"Lv{sys['level']}  HP:{sys['hp']}/{sys['max_hp']}",
                     PAL["dim"], self.F_SMALL)

        # ── Crew panel ──
        self.panel(30, 400, 540, 200)
        self.txt(40, 410, "CREW ROSTER", PAL["info"], self.F_MED)
        for ci, crew in enumerate(s["crew"][:8]):
            cy = 440 + ci * 22
            hp_pct = crew["hp"] / crew["max_hp"]
            hc = PAL["highlight"] if hp_pct > 0.5 else (PAL["warning"] if hp_pct > 0.25 else PAL["danger"])
            self.txt(50, cy, f"{crew['name']}", PAL["text"], self.F_BODY)
            self.txt(120, cy, f"({crew['species']})", PAL["dim"], self.F_SMALL)
            self.bar(210, cy, 70, 12, crew["hp"], crew["max_hp"], hc)
            self.txt(285, cy, f"{crew['hp']}/{crew['max_hp']}HP",
                     PAL["text"], self.F_TINY)
            self.txt(350, cy, f"Combat:{crew['combat']}  Repair:{crew['repair']}",
                     PAL["dim"], self.F_SMALL)
            self.txt(530, cy, SPECIES[crew['species']]['desc'],
                     PAL["dim"], self.F_TINY)

        # ── Weapons panel ──
        self.panel(590, 100, 580, 280)
        self.txt(600, 110, "WEAPONS LOADOUT", PAL["info"], self.F_MED)
        total_wpn_power = sum(WEAPONS[w]["power"] for w in s["weapons"])
        wpn_power_avail = s["systems"]["weapons"]["power"]
        self.txt(600, 135,
            f"Weapon power needed: {total_wpn_power}  |  Available: {wpn_power_avail}",
            PAL["warning"] if total_wpn_power > wpn_power_avail else PAL["text"], self.F_SMALL)

        for wi, wname in enumerate(s["weapons"][:7]):
            wy = 160 + wi * 32
            w = WEAPONS[wname]
            mf = " [MISSILE]" if w["missile"] else ""
            powered = wi < wpn_power_avail  # simplified: weapons powered in order
            pc = PAL["text"] if powered else PAL["dim"]
            self.txt(610, wy, f"{'●' if powered else '○'} {wname}",
                     pc, self.F_BODY)
            self.txt(610, wy + 14,
                f"  Dmg:{w['dmg']}×{w['shots']}  Pierce:{w['pierce']}  "
                f"Charge:{w['charge']}s  Pwr:{w['power']}{mf}",
                PAL["dim"], self.F_TINY)

            # Discard button
            if len(s["weapons"]) > 1:
                def discard(wn=wname):
                    s["weapons"].remove(wn)
                    self.show_ship_management()
                self.btn(1080, wy, 75, 26, "Discard", discard, "#442222")

        # ── Ship stats ──
        self.panel(590, 400, 580, 200)
        self.txt(600, 410, "SHIP STATS", PAL["info"], self.F_MED)
        evade = ship_evade(s)
        shields = ship_shield_layers(s)
        stats = [
            f"Ship: {s['name']}",
            f"Hull: {s['hull']} / {s['max_hull']}",
            f"Shield layers: {shields}  (from Shields power: {s['systems']['shields']['power']})",
            f"Evasion: {evade}%  (Engines Lv{s['systems']['engines']['power']} + Piloting Lv{s['systems']['piloting']['power']})",
            f"Reactor capacity: {s['max_reactor']} total power",
            f"Fuel: {s['fuel']}  |  Missiles: {s['missiles']}  |  Scrap: {s['scrap']}",
        ]
        for i, line in enumerate(stats):
            self.txt(610, 440 + i * 22, line, PAL["text"], self.F_BODY)

        # Back button
        self.btn(cx - 90, 620, 180, 45, "← Back to Map", self.show_sector_map, "#222244")

    # ══════════════════════════════════════════════════════════════════════════
    #  BEACON NAVIGATION
    # ══════════════════════════════════════════════════════════════════════════

    def jump_to(self, idx):
        self.ship["fuel"] -= 1
        self.current_beacon = idx
        self.beacons[idx]["visited"] = True
        b = self.beacons[idx]

        if b["type"] == "exit":
            self.sector_num += 1
            if self.sector_num >= SECTOR_COUNT:
                self.show_flagship_intro()
            else:
                self.show_jump_anim()
        elif b["type"] == "enemy":
            self.enemy = make_enemy(self.sector_num)
            self.init_combat()
        elif b["type"] == "event":
            self.show_event()
        elif b["type"] == "store":
            self.show_store()
        elif b["type"] == "empty":
            self.show_empty()

    def show_jump_anim(self):
        self.clear()
        cx = WIN_W // 2
        self.canvas.create_text(cx, WIN_H // 2 - 20,
            text=f"Jumping to Sector {self.sector_num + 1}...",
            fill=PAL["info"], font=self.F_BIG)
        for _ in range(50):
            sx, sy = random.randint(0, WIN_W), random.randint(0, WIN_H)
            self.canvas.create_line(sx, sy, sx + random.randint(30, 100), sy,
                fill="#3355aa", width=1)
        self.root.after(1200, self.start_sector)

    def show_empty(self):
        self.clear(); self.draw_top_bar()
        msgs = ["Nothing but the hum of your engines.", "Empty space. Peaceful, at least.",
                "A quiet beacon. Crew takes a breather.", "Sensors find nothing of interest."]
        self.txt(WIN_W // 2, 300, random.choice(msgs), PAL["dim"], self.F_BODY, "center")
        self.btn(WIN_W // 2 - 90, 370, 180, 42, "Continue", self.show_sector_map)

    def show_event(self):
        text, choices = get_random_event()
        self.clear(); self.draw_top_bar()
        cx = WIN_W // 2
        self.txt(cx, 85, "— EVENT —", PAL["warning"], self.F_BIG, "center")
        self.panel(cx - 380, 120, 760, 80)
        self.canvas.create_text(cx, 160, text=text,
            fill=PAL["text"], font=self.F_BODY, width=720)
        for i, (label, key) in enumerate(choices):
            def cmd(k=key): self.do_event(k)
            self.btn(cx - 270, 230 + i * 55, 540, 45, label, cmd)

    def do_event(self, key):
        msg, color_key = resolve_event(key, self.ship)
        self.clear(); self.draw_top_bar()
        cx = WIN_W // 2
        self.canvas.create_text(cx, 280, text=msg,
            fill=PAL.get(color_key, PAL["text"]), font=("Consolas", 14), width=700)
        if self.ship["hull"] <= 0 or not self.ship["crew"]:
            self.btn(cx - 90, 360, 180, 42, "Continue",
                     lambda: self.show_game_over(False, "Your ship is lost..."))
        else:
            self.btn(cx - 90, 360, 180, 42, "Continue", self.show_sector_map)

    # ── Store ──
    def show_store(self):
        self._store_weapons = random.sample(list(WEAPONS.keys()), min(3, len(WEAPONS)))
        self._store_msg = ""
        self._store_msg_col = PAL["text"]
        self._draw_store()

    def _draw_store(self):
        self.clear(); self.draw_top_bar()
        cx = WIN_W // 2; s = self.ship

        self.txt(cx, 70, "— STORE —", PAL["info"], self.F_BIG, "center")

        missing = s["max_hull"] - s["hull"]
        shield_cost = 50 + s["systems"]["shields"]["level"] * 30
        engine_cost = 30 + s["systems"]["engines"]["level"] * 20
        reactor_cost = 25 + s["max_reactor"] * 10
        pilot_cost = 25 + s["systems"]["piloting"]["level"] * 15

        items = [
            (f"Repair hull ({missing} HP needed) — 2 scrap/HP", "s_repair"),
            (f"Buy fuel ×5 — 15 scrap", "s_fuel"),
            (f"Buy missiles ×3 — 18 scrap", "s_missiles"),
            (f"Upgrade Shields → Lv{s['systems']['shields']['level']+1} — {shield_cost} scrap", "s_shields"),
            (f"Upgrade Engines → Lv{s['systems']['engines']['level']+1} — {engine_cost} scrap", "s_engines"),
            (f"Upgrade Piloting → Lv{s['systems']['piloting']['level']+1} — {pilot_cost} scrap", "s_pilot"),
            (f"Upgrade Reactor → {s['max_reactor']+1} bars — {reactor_cost} scrap", "s_reactor"),
        ]
        for wi, wn in enumerate(self._store_weapons):
            w = WEAPONS[wn]
            mf = " [M]" if w["missile"] else ""
            items.append((f"Buy {wn} (d:{w['dmg']}×{w['shots']} p:{w['pierce']}{mf}) — {w['cost']} scrap",
                          f"s_w{wi}"))

        for i, (label, key) in enumerate(items):
            by = 100 + i * 44
            def cmd(k=key): self.store_buy(k)
            self.btn(cx - 340, by, 680, 36, label, cmd)

        self.btn(cx - 90, 100 + len(items) * 44 + 12, 180, 42,
                 "Leave Store", self.show_sector_map, "#442222")

        if self._store_msg:
            self.canvas.create_text(cx, 100 + len(items) * 44 + 70,
                text=self._store_msg, fill=self._store_msg_col, font=self.F_BODY)

    def store_buy(self, key):
        s = self.ship
        if key == "s_repair":
            missing = s["max_hull"] - s["hull"]
            if missing == 0:
                self._store_msg = "Hull already full!"; self._store_msg_col = PAL["warning"]
            else:
                aff = min(missing, s["scrap"] // 2)
                if aff == 0:
                    self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
                else:
                    s["hull"] += aff; s["scrap"] -= aff * 2
                    self._store_msg = f"Repaired {aff} hull for {aff*2} scrap."
                    self._store_msg_col = PAL["highlight"]
        elif key == "s_fuel":
            if s["scrap"] >= 15:
                s["scrap"] -= 15; s["fuel"] += 5
                self._store_msg = "Bought 5 fuel."; self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key == "s_missiles":
            if s["scrap"] >= 18:
                s["scrap"] -= 18; s["missiles"] += 3
                self._store_msg = "Bought 3 missiles."; self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key == "s_shields":
            cost = 50 + s["systems"]["shields"]["level"] * 30
            if s["scrap"] >= cost:
                s["scrap"] -= cost
                sys = s["systems"]["shields"]
                sys["level"] += 1; sys["max_power"] = sys["level"]
                sys["max_hp"] = sys["level"] * 2; sys["hp"] = sys["max_hp"]
                self._store_msg = f"Shields upgraded to Lv{sys['level']}!"
                self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key == "s_engines":
            cost = 30 + s["systems"]["engines"]["level"] * 20
            if s["scrap"] >= cost:
                s["scrap"] -= cost
                sys = s["systems"]["engines"]
                sys["level"] += 1; sys["max_power"] = sys["level"]
                sys["max_hp"] = sys["level"] * 2; sys["hp"] = sys["max_hp"]
                self._store_msg = f"Engines upgraded to Lv{sys['level']}!"
                self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key == "s_pilot":
            cost = 25 + s["systems"]["piloting"]["level"] * 15
            if s["scrap"] >= cost:
                s["scrap"] -= cost
                sys = s["systems"]["piloting"]
                sys["level"] += 1; sys["max_power"] = sys["level"]
                sys["max_hp"] = sys["level"] * 2; sys["hp"] = sys["max_hp"]
                self._store_msg = f"Piloting upgraded to Lv{sys['level']}!"
                self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key == "s_reactor":
            cost = 25 + s["max_reactor"] * 10
            if s["scrap"] >= cost:
                s["scrap"] -= cost; s["max_reactor"] += 1
                self._store_msg = f"Reactor upgraded to {s['max_reactor']} bars!"
                self._store_msg_col = PAL["highlight"]
            else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        elif key.startswith("s_w"):
            wi = int(key[3:])
            if wi < len(self._store_weapons):
                wn = self._store_weapons[wi]; w = WEAPONS[wn]
                if s["scrap"] >= w["cost"]:
                    s["scrap"] -= w["cost"]; s["weapons"].append(wn)
                    self._store_weapons.pop(wi)
                    self._store_msg = f"Bought {wn}!"
                    self._store_msg_col = PAL["highlight"]
                else: self._store_msg = "Not enough scrap!"; self._store_msg_col = PAL["danger"]
        self._draw_store()

    # ══════════════════════════════════════════════════════════════════════════
    #  REAL-TIME COMBAT
    # ══════════════════════════════════════════════════════════════════════════

    def init_combat(self):
        """Set up and start real-time combat."""
        self.combat_running = True
        self.combat_paused = True   # start paused so player can review
        self.combat_over = False
        self.combat_log = [f"Engaging {self.enemy['name']}!  (PAUSED — press SPACE or click Unpause)"]
        self.player_weapon_charge = {w: 0.0 for w in self.ship["weapons"]}
        self.target_system = "shields"
        self.last_tick_time = time.time()
        self.shield_regen_timer = 0.0

        # Bind spacebar for pause toggle
        self.root.bind("<space>", self._toggle_pause_key)

        self.draw_combat()
        self.combat_tick()

    def _toggle_pause_key(self, event=None):
        if self.combat_running and not self.combat_over:
            self.combat_paused = not self.combat_paused
            if self.combat_paused:
                self.combat_log.append("── PAUSED ── Give orders, then unpause.")
            else:
                self.combat_log.append("── UNPAUSED ── Combat resumes!")
                self.last_tick_time = time.time()
            self.draw_combat()

    def combat_tick(self):
        """Main real-time loop — called ~20 times/sec."""
        if not self.combat_running:
            return

        now = time.time()
        if not self.combat_paused and not self.combat_over:
            dt = min(now - self.last_tick_time, 0.2)  # cap delta
            self.last_tick_time = now
            self._update_combat(dt)

        else:
            self.last_tick_time = now

        # Redraw at ~10fps for smoothness without overload
        self.draw_combat()
        self.combat_tick_id = self.root.after(100, self.combat_tick)

    def _update_combat(self, dt):
        """Advance combat simulation by dt seconds."""
        s = self.ship
        e = self.enemy
        sped = 1.5  # speed multiplier so fights aren't too slow

        # ── Player weapon charging ──
        wpn_sys = s["systems"]["weapons"]
        powered_slots = wpn_sys["power"]  # number of power bars allocated
        cumulative_power = 0
        for wname in s["weapons"]:
            w = WEAPONS[wname]
            cumulative_power += w["power"]
            if cumulative_power <= powered_slots:
                # This weapon is powered — charge it
                charge_rate = sped / max(w["charge"], 1)
                self.player_weapon_charge[wname] = min(
                    1.0, self.player_weapon_charge.get(wname, 0) + charge_rate * dt)

        # ── Enemy weapon charging & firing ──
        e_wpn = e["systems"]["weapons"]
        e_powered = e_wpn["power"]
        e_cum = 0
        for wname in e["weapons"]:
            w = WEAPONS[wname]
            e_cum += w["power"]
            if e_cum <= e_powered:
                e["weapon_charge"][wname] = e["weapon_charge"].get(wname, 0) + (sped / max(w["charge"], 1)) * dt
                if e["weapon_charge"][wname] >= 1.0:
                    e["weapon_charge"][wname] = 0.0
                    self._enemy_fires(wname)

        # ── Shield regen (every 4 seconds, shields try to regen 1 layer) ──
        self.shield_regen_timer += dt
        if self.shield_regen_timer >= 4.0:
            self.shield_regen_timer = 0.0
            # Player shield regen is automatic if shield system has power

        # ── Check end conditions ──
        if e["hull"] <= 0:
            self.combat_over = True
            self.combat_log.append(f">>> {e['name']} DESTROYED! <<<")
        if s["hull"] <= 0:
            self.combat_over = True
            self.combat_log.append(">>> YOUR SHIP IS DESTROYED! <<<")
        if not s["crew"]:
            self.combat_over = True
            self.combat_log.append(">>> ALL CREW LOST! <<<")

    def _enemy_fires(self, wname):
        """Enemy weapon fires at player."""
        s = self.ship
        e = self.enemy
        w = WEAPONS[wname]

        for shot in range(w["shots"]):
            # Evade check
            if random.randint(1, 100) <= ship_evade(s):
                self.combat_log.append(f"  Enemy {wname}: MISS!")
                continue

            shields = ship_shield_layers(s)
            eff_shields = max(0, shields - w["pierce"])
            dmg = max(0, w["dmg"] - eff_shields)

            if dmg > 0:
                # Random system damage
                target_sys = random.choice(SYSTEM_NAMES)
                sys_obj = s["systems"][target_sys]
                sys_dmg = random.randint(0, 1)
                if sys_dmg and sys_obj["hp"] > 0:
                    sys_obj["hp"] -= 1
                    # Cap power at effective max
                    eff_max = max(0, sys_obj["level"] - max(0, sys_obj["max_hp"] - sys_obj["hp"]))
                    if sys_obj["power"] > eff_max:
                        sys_obj["power"] = eff_max
                    self.combat_log.append(
                        f"  Enemy {wname}: {dmg} hull dmg + {SYSTEM_LABELS[target_sys]} damaged!")
                else:
                    self.combat_log.append(f"  Enemy {wname}: {dmg} hull dmg!")
                s["hull"] -= dmg

                # Crew injury chance
                if random.random() < 0.12 and s["crew"]:
                    victim = random.choice(s["crew"])
                    inj = random.randint(10, 25)
                    victim["hp"] -= inj
                    if victim["hp"] <= 0:
                        s["crew"].remove(victim)
                        self.combat_log.append(f"  {victim['name']} the {victim['species']} has been killed!")
                    else:
                        self.combat_log.append(f"  {victim['name']} takes {inj} injury ({victim['hp']}HP)")
            else:
                self.combat_log.append(f"  Enemy {wname}: blocked by shields!")

    def player_fire(self, wname):
        """Player fires a weapon (must be fully charged)."""
        if self.combat_over:
            return
        s = self.ship
        e = self.enemy
        w = WEAPONS[wname]

        if self.player_weapon_charge.get(wname, 0) < 1.0:
            return  # not charged

        if w["missile"] and s["missiles"] <= 0:
            self.combat_log.append(f"No missiles remaining!")
            return

        if w["missile"]:
            s["missiles"] -= 1

        self.player_weapon_charge[wname] = 0.0

        target_sn = self.target_system
        e_evade = e["evade"]
        # Reduce evade if engines are damaged
        e_eng = e["systems"]["engines"]
        e_evade = int(e_evade * (e_eng["power"] / max(e_eng["max_power"], 1)))

        for shot in range(w["shots"]):
            if random.randint(1, 100) <= e_evade:
                self.combat_log.append(f"  {wname}: MISS!")
                continue

            e_shields = e["systems"]["shields"]["power"]
            eff_shields = max(0, e_shields - w["pierce"])
            dmg = max(0, w["dmg"] - eff_shields)

            if dmg > 0:
                e["hull"] -= dmg
                # Damage targeted system
                t_sys = e["systems"].get(target_sn)
                if t_sys and t_sys["hp"] > 0:
                    t_sys["hp"] -= 1
                    eff_max = max(0, t_sys["level"] - max(0, t_sys["max_hp"] - t_sys["hp"]))
                    if t_sys["power"] > eff_max:
                        t_sys["power"] = eff_max
                    self.combat_log.append(
                        f"  {wname} → {SYSTEM_LABELS[target_sn]}: {dmg} hull + system hit!")
                else:
                    self.combat_log.append(f"  {wname}: {dmg} hull dmg!")
            else:
                self.combat_log.append(f"  {wname}: blocked by shields!")

        if not self.combat_paused:
            self.draw_combat()

    def draw_combat(self):
        """Redraw the entire combat screen."""
        self.canvas.delete("all")
        draw_stars(self.canvas, 100)
        self.draw_top_bar()
        s = self.ship
        e = self.enemy

        paused = self.combat_paused and not self.combat_over

        # ── Title bar ──
        status = "PAUSED" if paused else ("COMBAT OVER" if self.combat_over else "REAL-TIME")
        sc = PAL["warning"] if paused else (PAL["danger"] if not self.combat_over else PAL["highlight"])
        self.txt(WIN_W // 2, 62, f"— COMBAT: {e['name']} — [{status}]",
                 sc, self.F_MED, "center")

        # ═══ LEFT: Player ship ═══
        self.panel(15, 82, 370, 320)
        self.txt(25, 90, s["name"], PAL["p_ship"], self.F_MED)

        # Pixel art
        draw_pixel_art(self.canvas, SHIP_PLAYER, 30, 115, 3, "ps")

        # Hull
        self.txt(170, 115, "Hull:", PAL["dim"], self.F_SMALL)
        self.bar(210, 113, 150, 14, s["hull"], s["max_hull"], PAL["hull"])
        self.txt(365, 115, f"{s['hull']}/{s['max_hull']}", PAL["text"], self.F_TINY)

        # Systems
        self.txt(170, 140, "Systems:", PAL["dim"], self.F_SMALL)
        for si, sn in enumerate(SYSTEM_NAMES):
            sy = 160 + si * 24
            sys_o = s["systems"][sn]
            self.txt(175, sy, SYSTEM_LABELS[sn][:7], PAL["text"], self.F_TINY)
            for pi in range(sys_o["max_power"]):
                px = 230 + pi * 14
                col = PAL["power_on"] if pi < sys_o["power"] else PAL["power_off"]
                self.canvas.create_rectangle(px, sy, px + 11, sy + 12,
                    fill=col, outline=PAL["border"])
            hc = PAL["sys_ok"] if sys_o["hp"] >= sys_o["max_hp"] else PAL["sys_dmg"]
            self.bar(310, sy, 50, 12, sys_o["hp"], sys_o["max_hp"], hc)

        # Crew
        self.txt(170, 285, "Crew:", PAL["dim"], self.F_TINY)
        for ci, crew in enumerate(s["crew"][:5]):
            self.txt(210 + ci * 32, 285,
                f"{crew['name'][0]}({crew['species'][0]})", PAL["text"], self.F_TINY)
        self.txt(170, 305, f"Evade: {ship_evade(s)}%   Shields: {ship_shield_layers(s)} layers",
                 PAL["dim"], self.F_TINY)

        # Power allocation buttons (only when paused)
        if paused:
            self.txt(25, 325, "Power (paused):", PAL["warning"], self.F_TINY)
            for si, sn in enumerate(SYSTEM_NAMES):
                bx = 25 + si * 72
                def add_p(name=sn):
                    ss = s["systems"][name]
                    eff_max = max(0, ss["level"] - max(0, ss["max_hp"] - ss["hp"]))
                    if ss["power"] < eff_max and total_power_used(s) < s["max_reactor"]:
                        ss["power"] += 1
                def sub_p(name=sn):
                    ss = s["systems"][name]
                    if ss["power"] > 0: ss["power"] -= 1
                self.btn(bx, 340, 16, 16, "+", add_p, "#224422")
                self.btn(bx + 18, 340, 16, 16, "-", sub_p, "#442222")
                self.txt(bx + 36, 342, sn[:3].upper(), PAL["dim"], self.F_TINY)

        # ═══ RIGHT: Enemy ship ═══
        self.panel(780, 82, 405, 320)
        self.txt(790, 90, e["name"], PAL["e_ship"], self.F_MED)

        enemy_art = SHIP_FLAGSHIP if e.get("is_flagship") else SHIP_ENEMY
        esc = 3 if e.get("is_flagship") else 3
        eaw = len(enemy_art[0]) * esc
        draw_pixel_art(self.canvas, enemy_art, 1160 - eaw, 115, esc, "es")

        # Hull
        self.txt(790, 115, "Hull:", PAL["dim"], self.F_SMALL)
        self.bar(830, 113, 150, 14, e["hull"], e["max_hull"], PAL["danger"])
        self.txt(985, 115, f"{e['hull']}/{e['max_hull']}", PAL["text"], self.F_TINY)

        # Enemy systems
        self.txt(790, 140, "Systems:", PAL["dim"], self.F_SMALL)
        e_sys_names = ["shields", "weapons", "engines"]
        for si, sn in enumerate(e_sys_names):
            sy = 160 + si * 24
            sys_o = e["systems"][sn]
            self.txt(795, sy, SYSTEM_LABELS[sn][:7], PAL["text"], self.F_TINY)
            for pi in range(sys_o["max_power"]):
                px = 850 + pi * 14
                col = PAL["power_on"] if pi < sys_o["power"] else PAL["power_off"]
                self.canvas.create_rectangle(px, sy, px + 11, sy + 12,
                    fill=col, outline=PAL["border"])
            hc = PAL["sys_ok"] if sys_o["hp"] >= sys_o["max_hp"] else PAL["sys_dmg"]
            self.bar(950, sy, 50, 12, sys_o["hp"], sys_o["max_hp"], hc)

        # Enemy weapons & charge bars
        self.txt(790, 240, "Weapons:", PAL["dim"], self.F_SMALL)
        for wi, wn in enumerate(e["weapons"][:4]):
            wy = 258 + wi * 20
            ch = e["weapon_charge"].get(wn, 0)
            self.txt(795, wy, wn[:18], PAL["text"], self.F_TINY)
            self.bar(920, wy, 60, 10, ch, 1.0,
                     PAL["danger"] if ch > 0.8 else PAL["charge_fg"],
                     PAL["charge_bg"])

        self.txt(790, 340, f"Evade: {e['evade']}%", PAL["dim"], self.F_TINY)

        # ═══ CENTER: Target selector ═══
        self.panel(395, 82, 375, 155)
        self.txt(405, 90, "TARGET SYSTEM", PAL["warning"], self.F_MED)
        self.txt(405, 110, "Choose which enemy system to focus fire on:",
                 PAL["dim"], self.F_TINY)
        targets = ["shields", "weapons", "engines"]
        for ti, tn in enumerate(targets):
            tx = 410 + ti * 120
            selected = (tn == self.target_system)
            col = "#334422" if selected else PAL["btn"]
            border_col = PAL["highlight"] if selected else PAL["btn_border"]
            def sel_cmd(t=tn):
                self.target_system = t
            self.btn(tx, 130, 110, 32, SYSTEM_LABELS[tn], sel_cmd, col)
            if selected:
                self.canvas.create_rectangle(tx, 130, tx + 110, 162,
                    fill="", outline=PAL["highlight"], width=2)

        # Target info
        t_sys = e["systems"][self.target_system]
        self.txt(405, 175,
            f"Target: {SYSTEM_LABELS[self.target_system]}  "
            f"Pwr: {t_sys['power']}/{t_sys['max_power']}  "
            f"HP: {t_sys['hp']}/{t_sys['max_hp']}",
            PAL["text"], self.F_SMALL)
        if t_sys["hp"] < t_sys["max_hp"]:
            self.txt(405, 195, "DAMAGED — reduced effectiveness!",
                     PAL["danger"], self.F_TINY)

        # ═══ CENTER: Pause / Flee ═══
        if not self.combat_over:
            pause_label = "▶ UNPAUSE (Space)" if paused else "❚❚ PAUSE (Space)"
            pause_col = "#224422" if paused else "#442222"
            self.btn(440, 250, 180, 38, pause_label, self._toggle_pause_key, pause_col)

            if not e.get("is_flagship"):
                flee_chance = ship_evade(s) + 20
                self.btn(440, 295, 180, 38, f"FLEE ({flee_chance}%)",
                         self._try_flee, "#331111")

            # Repair ship button (crew auto-repair during combat)
            if paused and s["crew"]:
                repair_amt = max(1, sum(c["repair"] for c in s["crew"]) // 6)
                self.btn(440, 340, 180, 36,
                    f"Crew Repair +{repair_amt}HP",
                    lambda: self._crew_repair(repair_amt), "#1a3322")

        # ═══ BOTTOM LEFT: Player weapons ═══
        self.panel(15, 410, 570, 195)
        self.txt(25, 418, "YOUR WEAPONS", PAL["info"], self.F_MED)
        self.txt(25, 436, "Click a charged weapon to fire! Weapons auto-charge when powered.",
                 PAL["dim"], self.F_TINY)

        wpn_power = s["systems"]["weapons"]["power"]
        cum_power = 0
        for wi, wname in enumerate(s["weapons"][:6]):
            w = WEAPONS[wname]
            cum_power += w["power"]
            wy = 455 + wi * 29
            is_powered = cum_power <= wpn_power
            charge = self.player_weapon_charge.get(wname, 0)
            is_ready = charge >= 1.0 and is_powered

            # Charge bar
            cbar_color = PAL["charge_fg"] if is_powered else PAL["sys_off"]
            if charge >= 1.0:
                cbar_color = PAL["highlight"]
            self.bar(30, wy, 90, 16, charge, 1.0, cbar_color, PAL["charge_bg"])

            mf = " [M]" if w["missile"] else ""
            status = " READY!" if is_ready else (f" {int(charge*100)}%" if is_powered else " NO POWER")
            label_text = f"{wname} d:{w['dmg']}×{w['shots']}{mf}{status}"

            if is_ready and not self.combat_over:
                def fire(wn=wname): self.player_fire(wn)
                self.btn(125, wy - 2, 440, 22, label_text, fire, "#1a3322")
            else:
                fc = PAL["text"] if is_powered else PAL["dim"]
                self.txt(130, wy, label_text, fc, self.F_SMALL)

        # Resources
        self.txt(25, 585, f"Missiles: {s['missiles']}", PAL["missile_c"], self.F_SMALL)

        # ═══ BOTTOM RIGHT: Combat log ═══
        self.panel(595, 410, 590, 195)
        self.txt(605, 418, "COMBAT LOG", PAL["info"], ("Consolas", 10, "bold"))
        visible = self.combat_log[-9:]
        for li, line in enumerate(visible):
            col = PAL["text"]
            if "MISS" in line or "blocked" in line: col = PAL["warning"]
            elif "hull" in line.lower() or "killed" in line or "DESTROYED" in line: col = PAL["danger"]
            elif "PAUSED" in line or "UNPAUSE" in line: col = PAL["warning"]
            elif "Repaired" in line: col = PAL["highlight"]
            self.txt(610, 438 + li * 17, line[:90], col, self.F_TINY)

        # ═══ BOTTOM: Combat over buttons ═══
        if self.combat_over:
            self.panel(395, 620, 410, 60)
            if e["hull"] <= 0:
                self.txt(600, 630, f"Victory! +{e['scrap']} scrap, +{e['fuel']} fuel",
                         PAL["highlight"], self.F_BODY, "center")
                def collect():
                    s["scrap"] += e["scrap"]; s["fuel"] += e["fuel"]
                    s["missiles"] += e["missiles"]
                    self.combat_running = False
                    self.root.unbind("<space>")
                    if e.get("is_flagship"):
                        self._flagship_phase_done()
                    else:
                        self.show_sector_map()
                self.btn(520, 655, 160, 36, "Collect & Continue", collect, "#1a4430")
            else:
                self.txt(600, 640, "Your ship has been lost...",
                         PAL["danger"], self.F_BODY, "center")
                def go_over():
                    self.combat_running = False
                    self.root.unbind("<space>")
                    self.show_game_over(False, "Your ship was destroyed in combat!")
                self.btn(520, 662, 160, 36, "Continue", go_over, "#441111")

    def _try_flee(self):
        s = self.ship
        flee_chance = ship_evade(s) + 20
        if random.randint(1, 100) <= flee_chance:
            self.combat_log.append("FTL drive engaged — escaped!")
            s["fuel"] -= 1
            self.combat_running = False
            self.root.unbind("<space>")
            self.combat_over = True
            self.clear(); self.draw_top_bar()
            self.txt(WIN_W // 2, 300, "You escaped!", PAL["warning"], self.F_BIG, "center")
            self.btn(WIN_W // 2 - 90, 370, 180, 42, "Continue", self.show_sector_map)
        else:
            self.combat_log.append("FTL charging... not fast enough!")

    def _crew_repair(self, amount):
        """Repair hull during pause."""
        s = self.ship
        s["hull"] = min(s["hull"] + amount, s["max_hull"])
        self.combat_log.append(f"Crew repairs {amount} hull. ({s['hull']}/{s['max_hull']})")

    # ══════════════════════════════════════════════════════════════════════════
    #  FLAGSHIP
    # ══════════════════════════════════════════════════════════════════════════

    def show_flagship_intro(self):
        self.clear()
        cx = WIN_W // 2
        self.canvas.create_text(cx, 90, text="THE LAST STAND",
            fill=PAL["danger"], font=("Consolas", 36, "bold"))
        self.canvas.create_text(cx, 170,
            text="You've reached Federation HQ — but the Rebel\n"
                 "Flagship has arrived first.\n\n"
                 "Defeat the Flagship in THREE PHASES to save the Federation!\n"
                 "Each phase, the flagship reconfigures with new weapons.",
            fill=PAL["text"], font=self.F_BODY, justify="center", width=650)
        aw = len(SHIP_FLAGSHIP[0]) * PX * 2
        draw_pixel_art(self.canvas, SHIP_FLAGSHIP, cx - aw // 2, 300, PX * 2)
        self.btn(cx - 120, 560, 240, 55, "ENGAGE FLAGSHIP", self._start_flagship, "#441111")

    def _start_flagship(self):
        self.flagship_phase = 1
        self._begin_flagship_phase()

    def _begin_flagship_phase(self):
        phase = self.flagship_phase
        s = self.ship

        # Phase effects
        if phase == 2 and s["crew"]:
            victim = random.choice(s["crew"])
            victim["hp"] -= 30
            if victim["hp"] <= 0:
                s["crew"].remove(victim)
        elif phase == 3:
            sh = s["systems"]["shields"]
            if sh["power"] > 0: sh["power"] -= 1

        self.enemy = make_flagship(phase)
        self.init_combat()

    def _flagship_phase_done(self):
        s = self.ship
        if self.flagship_phase >= 3:
            self.show_game_over(True)
            return

        # Heal between phases
        s["hull"] = min(s["hull"] + 8, s["max_hull"])
        # Repair all systems 1 HP
        for sn in SYSTEM_NAMES:
            sys_o = s["systems"][sn]
            sys_o["hp"] = min(sys_o["hp"] + 1, sys_o["max_hp"])

        self.clear(); self.draw_top_bar()
        cx = WIN_W // 2
        phase = self.flagship_phase
        self.txt(cx, 200, f"Phase {phase} complete!",
                 PAL["highlight"], self.F_BIG, "center")
        self.txt(cx, 250, f"Hull repaired +8. Systems repaired +1 HP.\nPreparing Phase {phase + 1}...",
                 PAL["text"], self.F_BODY, "center")

        def next_phase():
            self.flagship_phase += 1
            self._begin_flagship_phase()
        self.btn(cx - 120, 320, 240, 50, f"Begin Phase {phase + 1}", next_phase, "#441111")

    # ══════════════════════════════════════════════════════════════════════════
    #  GAME OVER / VICTORY
    # ══════════════════════════════════════════════════════════════════════════

    def show_game_over(self, won, reason=""):
        self.clear()
        try:
            self.root.unbind("<space>")
        except Exception:
            pass
        cx = WIN_W // 2

        if won:
            self.canvas.create_text(cx, 120, text="★  VICTORY  ★",
                fill=PAL["highlight"], font=("Consolas", 44, "bold"))
            self.canvas.create_text(cx, 230,
                text="The Rebel Flagship crumbles in a brilliant explosion.\n"
                     "Your crew cheers as the Federation fleet rallies.\n"
                     "The critical data has been delivered.\n\n"
                     "Against all odds, the Federation survives.\n"
                     "Congratulations, Commander!",
                fill=PAL["text"], font=self.F_BODY, justify="center", width=600)
        else:
            self.canvas.create_text(cx, 120, text="GAME OVER",
                fill=PAL["danger"], font=("Consolas", 44, "bold"))
            if reason:
                self.canvas.create_text(cx, 185, text=reason,
                    fill=PAL["warning"], font=self.F_BODY)
            self.canvas.create_text(cx, 270,
                text="Your ship breaks apart, debris scattering into the void.\n"
                     "The Rebellion's advance continues unchecked.\n"
                     "The Federation falls.",
                fill=PAL["text"], font=self.F_BODY, justify="center", width=600)

        if self.ship:
            self.canvas.create_text(cx, 400,
                text=f"Ship: {self.ship['name']}    Crew: {len(self.ship['crew'])} surviving    "
                     f"Scrap: {self.ship['scrap']}    Sector: {self.sector_num + 1}",
                fill=PAL["dim"], font=self.F_BODY)

        self.btn(cx - 200, 480, 180, 50, "Play Again", self.restart, "#1a4430")
        self.btn(cx + 20, 480, 180, 50, "Quit", self.root.destroy, "#441111")

    def restart(self):
        self.ship = None
        self.sector_num = 0
        self.flagship_phase = 0
        self.show_title()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = FTLApp(root)
    root.mainloop()
