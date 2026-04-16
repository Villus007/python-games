"""
Metro Tycoon — A Mini Metro-style Transit Puzzle Game
=====================================================
Build efficient rail lines, manage different types of trains,
and keep passengers moving in your growing metro network!

Features 3 train types — Commuter, Intercity, and High Speed —
each with multiple unlockable models.  Earn points to unlock
new models and money to purchase them.

Controls:
  • Left-click stations to build / extend lines
  • Right-click or Escape to finish / cancel building
  • Space to pause / resume
  • 1x / 2x / 3x speed toggle in the HUD

Built with tkinter — no external dependencies.
"""

import tkinter as tk
from tkinter import font as tkfont
import random, math, time

# ═══════════════════════════════════════════════════════════════════════════════
#  WINDOW & LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

WIN_W, WIN_H = 1280, 800
HUD_H   = 48
MAP_W   = 880
PANEL_X = MAP_W
PANEL_W = WIN_W - MAP_W          # 400
MAP_Y   = HUD_H
MAP_H   = WIN_H - HUD_H          # 752

# play-area margins (station placement)
MAP_PAD    = 50
PLAY_LEFT  = MAP_PAD
PLAY_TOP   = MAP_Y + MAP_PAD
PLAY_RIGHT = MAP_W - MAP_PAD
PLAY_BOT   = WIN_H - MAP_PAD

# ═══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════

C_MAP_BG       = "#f5f0e1"
C_RIVER        = "#a8cce0"
C_RIVER_EDGE   = "#7fb3cc"

C_HUD_BG       = "#1a1a2e"
C_HUD_TEXT     = "#e0e0e0"
C_PANEL_BG     = "#16213e"
C_PANEL_SEC    = "#1a1a3e"
C_PANEL_TEXT   = "#d0d0e0"
C_PANEL_DIM    = "#6070a0"
C_PANEL_BRIGHT = "#ffffff"
C_PANEL_BTN    = "#0f3460"
C_PANEL_BTN_HI = "#1a5276"
C_PANEL_BTN_TX = "#e0e0e0"
C_PANEL_SEP    = "#2a3f6f"

C_ST_FILL      = "#ffffff"
C_ST_LINE      = "#333333"
C_ST_WARN      = "#ff8c42"
C_ST_CRIT      = "#e63946"

C_COMMUTER     = "#27ae60"
C_INTERCITY    = "#2980b9"
C_HIGHSPEED    = "#c0392b"
C_GOLD         = "#f1c40f"
C_SCORE        = "#2ecc71"
C_LOCKED       = "#555555"

LINE_COLORS = [
    "#e63946", "#457b9d", "#2a9d8f", "#e9c46a",
    "#f4a261", "#7b2d8e", "#264653", "#606c38",
]
LINE_NAMES = [
    "Red", "Blue", "Teal", "Gold",
    "Orange", "Purple", "Navy", "Olive",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  SHAPES
# ═══════════════════════════════════════════════════════════════════════════════

SHAPES = ["circle", "triangle", "square", "diamond", "star", "pentagon"]
SHAPE_COLORS = {
    "circle":   "#e63946",
    "triangle": "#2a9d8f",
    "square":   "#457b9d",
    "diamond":  "#e9c46a",
    "star":     "#f4a261",
    "pentagon": "#7b2d8e",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  TRAIN MODEL DATA
# ═══════════════════════════════════════════════════════════════════════════════

TRAIN_MODELS = {
    "commuter": {
        "Local Shuttle":  {"speed":  55, "capacity":  4, "unlock_pts":    0, "cost":    0},
        "Metro Liner":    {"speed":  70, "capacity":  5, "unlock_pts":  100, "cost":   60},
        "Urban Express":  {"speed":  85, "capacity":  6, "unlock_pts":  350, "cost":  140},
        "City Sprinter":  {"speed": 100, "capacity":  8, "unlock_pts":  700, "cost":  240},
    },
    "intercity": {
        "Regional":       {"speed":  80, "capacity":  6, "unlock_pts":  150, "cost":  120},
        "Cross-City":     {"speed": 100, "capacity":  7, "unlock_pts":  450, "cost":  200},
        "Express IC":     {"speed": 125, "capacity":  9, "unlock_pts":  800, "cost":  320},
        "Premier IC":     {"speed": 150, "capacity": 11, "unlock_pts": 1400, "cost":  480},
    },
    "highspeed": {
        "Bullet Train":   {"speed": 140, "capacity":  8, "unlock_pts":  500, "cost":  300},
        "Maglev":         {"speed": 175, "capacity": 10, "unlock_pts": 1000, "cost":  450},
        "Hyperloop":      {"speed": 210, "capacity": 13, "unlock_pts": 1800, "cost":  700},
        "Quantum Rail":   {"speed": 260, "capacity": 16, "unlock_pts": 3000, "cost": 1100},
    },
}

TYPE_LABELS = {"commuter": "Commuter", "intercity": "Intercity", "highspeed": "High Speed"}
TYPE_COLORS = {"commuter": C_COMMUTER, "intercity": C_INTERCITY, "highspeed": C_HIGHSPEED}
TYPE_ICONS  = {"commuter": "\U0001f68b", "intercity": "\U0001f686", "highspeed": "\U0001f684"}

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

STATION_CAP         = 10        # passengers before overflow warning
OVERFLOW_LIMIT      = 45.0      # seconds of overflow → game over
MIN_STATION_DIST    = 105
INITIAL_STATIONS    = 3
MAX_LINES           = 8
STATION_SPAWN_BASE  = 18.0
PASSENGER_SPAWN_BASE= 3.5
LOAD_TIME_BASE      = 0.35
LOAD_TIME_PER_PAX   = 0.07
PTS_PER_DELIVERY    = 10
MONEY_PER_DELIVERY  = 8
STARTING_MONEY      = 150
STATION_SZ          = 18
PAX_SZ              = 6
FPS                 = 30

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER — draw a geometric shape centred at (cx, cy)
# ═══════════════════════════════════════════════════════════════════════════════

def draw_shape(canvas, shape, cx, cy, sz, tags="", **kw):
    if shape == "circle":
        return canvas.create_oval(cx-sz, cy-sz, cx+sz, cy+sz, tags=tags, **kw)
    elif shape == "triangle":
        p = [cx, cy-sz, cx-sz*0.87, cy+sz*0.5, cx+sz*0.87, cy+sz*0.5]
        return canvas.create_polygon(p, tags=tags, **kw)
    elif shape == "square":
        s = sz * 0.82
        return canvas.create_rectangle(cx-s, cy-s, cx+s, cy+s, tags=tags, **kw)
    elif shape == "diamond":
        p = [cx, cy-sz, cx+sz*0.65, cy, cx, cy+sz, cx-sz*0.65, cy]
        return canvas.create_polygon(p, tags=tags, **kw)
    elif shape == "star":
        p = []
        for i in range(5):
            a  = math.radians(i*72 - 90)
            p += [cx + sz*math.cos(a), cy + sz*math.sin(a)]
            a2 = math.radians(i*72 + 36 - 90)
            p += [cx + sz*0.42*math.cos(a2), cy + sz*0.42*math.sin(a2)]
        return canvas.create_polygon(p, tags=tags, **kw)
    elif shape == "pentagon":
        p = []
        for i in range(5):
            a = math.radians(i*72 - 90)
            p += [cx + sz*math.cos(a), cy + sz*math.sin(a)]
        return canvas.create_polygon(p, tags=tags, **kw)

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME ENTITY CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class Station:
    _nid = 0
    def __init__(self, x, y, shape):
        Station._nid += 1
        self.id    = Station._nid
        self.x, self.y = x, y
        self.shape = shape
        self.passengers  = []
        self.capacity    = STATION_CAP
        self.overflow_t  = 0.0
        self.pulse       = 0.0          # animation counter

class Passenger:
    __slots__ = ("desired_shape", "wait")
    def __init__(self, desired_shape):
        self.desired_shape = desired_shape
        self.wait = 0.0

class MetroLine:
    _nid = 0
    def __init__(self, color_idx):
        MetroLine._nid += 1
        self.id         = MetroLine._nid
        self.color_idx  = color_idx
        self.color      = LINE_COLORS[color_idx]
        self.name       = LINE_NAMES[color_idx]
        self.stations   = []
        self.trains     = []

class Train:
    _nid = 0
    def __init__(self, ttype, model):
        Train._nid += 1
        self.id         = Train._nid
        self.ttype      = ttype
        self.model      = model
        d = TRAIN_MODELS[ttype][model]
        self.speed      = d["speed"]
        self.capacity   = d["capacity"]
        self.passengers = []
        self.line       = None
        # movement
        self.seg        = 0
        self.prog       = 0.0
        self.dir        = 1
        self.at_st      = True
        self.st_idx     = 0
        self.load_t     = 0.0
        self.x = self.y = 0.0

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME STATE / LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

class GameState:
    def __init__(self):
        self.stations       = []
        self.lines          = []
        self.all_trains     = []
        self.unassigned     = []
        self.money          = STARTING_MONEY
        self.points         = 0
        self.score          = 0
        self.delivered      = 0
        self.elapsed        = 0.0
        self.game_over      = False
        self.paused         = False
        self.over_reason    = ""
        self.station_timer  = 8.0
        self.pax_timer      = 2.0
        self.st_interval    = STATION_SPAWN_BASE
        self.pax_interval   = PASSENGER_SPAWN_BASE
        self.used_colors    = set()
        self._init_stations()
        # free starter train
        t = Train("commuter", "Local Shuttle")
        self.all_trains.append(t)
        self.unassigned.append(t)

    # ---------- stations ---------------------------------------------------

    def _init_stations(self):
        for i in range(INITIAL_STATIONS):
            self._place_station(SHAPES[i % len(SHAPES)])

    def _place_station(self, shape=None):
        if shape is None:
            have = {s.shape for s in self.stations}
            miss = [s for s in SHAPES if s not in have]
            shape = random.choice(miss) if miss and random.random() < 0.65 else random.choice(SHAPES)
        for _ in range(300):
            x = random.randint(PLAY_LEFT, PLAY_RIGHT)
            y = random.randint(PLAY_TOP, PLAY_BOT)
            if all(math.hypot(s.x-x, s.y-y) >= MIN_STATION_DIST for s in self.stations):
                st = Station(x, y, shape)
                self.stations.append(st)
                return st
        return None

    # ---------- main update ------------------------------------------------

    def update(self, dt):
        if self.paused or self.game_over:
            return
        self.elapsed += dt
        t = self.elapsed
        self.st_interval  = max(8,   STATION_SPAWN_BASE  - t * 0.018)
        self.pax_interval = max(0.9, PASSENGER_SPAWN_BASE - t * 0.007)

        self.station_timer -= dt
        if self.station_timer <= 0:
            self.station_timer = self.st_interval + random.uniform(-2, 2)
            self._place_station()

        self.pax_timer -= dt
        if self.pax_timer <= 0:
            self.pax_timer = self.pax_interval + random.uniform(-0.3, 0.3)
            self._spawn_pax()

        for tr in self.all_trains:
            if tr.line:
                self._move_train(tr, dt)

        for st in self.stations:
            st.pulse += dt * 3
            if len(st.passengers) > st.capacity:
                st.overflow_t += dt
                if st.overflow_t >= OVERFLOW_LIMIT:
                    self.game_over = True
                    self.over_reason = f"Station overcrowded! ({st.shape.title()})"
            else:
                st.overflow_t = max(0, st.overflow_t - dt * 0.5)
            for p in st.passengers:
                p.wait += dt

    # ---------- passenger --------------------------------------------------

    def _spawn_pax(self):
        if not self.stations:
            return
        st = random.choice(self.stations)
        others = [s for s in SHAPES if s != st.shape]
        exist  = [s.shape for s in self.stations if s.shape != st.shape]
        shape  = random.choice(exist) if exist else random.choice(others)
        st.passengers.append(Passenger(shape))

    # ---------- train movement ---------------------------------------------

    def _move_train(self, tr, dt):
        line = tr.line
        n = len(line.stations)
        if n < 2:
            if line.stations:
                tr.x, tr.y = line.stations[0].x, line.stations[0].y
            return

        if tr.at_st:
            tr.load_t -= dt
            if tr.load_t <= 0:
                tr.at_st = False
                if tr.dir == 1:
                    if tr.st_idx >= n - 1:
                        tr.dir = -1
                        tr.seg  = tr.st_idx - 1
                        tr.prog = 1.0
                    else:
                        tr.seg  = tr.st_idx
                        tr.prog = 0.0
                else:
                    if tr.st_idx <= 0:
                        tr.dir = 1
                        tr.seg  = 0
                        tr.prog = 0.0
                    else:
                        tr.seg  = tr.st_idx - 1
                        tr.prog = 1.0
            if 0 <= tr.st_idx < n:
                s = line.stations[tr.st_idx]
                tr.x, tr.y = s.x, s.y
            return

        seg = tr.seg
        if seg < 0 or seg >= n - 1:
            tr.at_st = True; tr.st_idx = 0; tr.seg = 0; tr.prog = 0.0
            if line.stations:
                tr.x, tr.y = line.stations[0].x, line.stations[0].y
            return

        s1, s2 = line.stations[seg], line.stations[seg+1]
        d = max(1, math.hypot(s2.x - s1.x, s2.y - s1.y))
        dp = tr.speed * dt / d

        if tr.dir == 1:
            tr.prog += dp
            if tr.prog >= 1.0:
                tr.prog = 1.0; tr.at_st = True; tr.st_idx = seg + 1
                self._train_arrive(tr, line.stations[tr.st_idx])
        else:
            tr.prog -= dp
            if tr.prog <= 0.0:
                tr.prog = 0.0; tr.at_st = True; tr.st_idx = seg
                self._train_arrive(tr, line.stations[tr.st_idx])

        tr.x = s1.x + (s2.x - s1.x) * tr.prog
        tr.y = s1.y + (s2.y - s1.y) * tr.prog

    def _train_arrive(self, tr, st):
        # unload
        deliv = [p for p in tr.passengers if p.desired_shape == st.shape]
        tr.passengers = [p for p in tr.passengers if p.desired_shape != st.shape]
        for _ in deliv:
            self.score    += PTS_PER_DELIVERY
            self.points   += PTS_PER_DELIVERY
            self.money    += MONEY_PER_DELIVERY
            self.delivered += 1
        # load (smart: only if line visits that shape)
        loaded = 0; stay = []
        line_shapes = {s.shape for s in tr.line.stations}
        for p in st.passengers:
            if len(tr.passengers) < tr.capacity and p.desired_shape in line_shapes:
                tr.passengers.append(p); loaded += 1
            else:
                stay.append(p)
        st.passengers = stay
        tr.load_t = LOAD_TIME_BASE + (len(deliv) + loaded) * LOAD_TIME_PER_PAX

    # ---------- line management --------------------------------------------

    def create_line(self, stations):
        for i in range(MAX_LINES):
            if i not in self.used_colors:
                ln = MetroLine(i)
                ln.stations = list(stations)
                self.lines.append(ln)
                self.used_colors.add(i)
                return ln
        return None

    def delete_line(self, ln):
        for tr in list(ln.trains):
            tr.line = None; tr.at_st = True; tr.st_idx = 0
            tr.seg = 0; tr.prog = 0.0; tr.passengers.clear()
            self.unassigned.append(tr)
        ln.trains.clear()
        self.used_colors.discard(ln.color_idx)
        if ln in self.lines:
            self.lines.remove(ln)

    def add_station_to_line(self, ln, st):
        if st not in ln.stations:
            ln.stations.append(st)
            self._reset_line_trains(ln)

    def remove_last_station(self, ln):
        if ln.stations:
            ln.stations.pop()
            self._reset_line_trains(ln)

    def _reset_line_trains(self, ln):
        for tr in ln.trains:
            tr.at_st = True; tr.st_idx = 0; tr.seg = 0
            tr.prog = 0.0; tr.dir = 1; tr.load_t = 0.3
            if ln.stations:
                tr.x, tr.y = ln.stations[0].x, ln.stations[0].y

    def assign_train(self, tr, ln):
        if tr in self.unassigned:
            self.unassigned.remove(tr)
        if tr.line:
            tr.line.trains.remove(tr)
        tr.line = ln; ln.trains.append(tr)
        tr.at_st = True; tr.st_idx = 0; tr.seg = 0
        tr.prog = 0.0; tr.dir = 1; tr.load_t = 0.3
        tr.passengers.clear()
        if ln.stations:
            tr.x, tr.y = ln.stations[0].x, ln.stations[0].y

    def unassign_train(self, tr):
        if tr.line:
            tr.line.trains.remove(tr)
        tr.line = None; tr.passengers.clear()
        if tr not in self.unassigned:
            self.unassigned.append(tr)

    # ---------- shop -------------------------------------------------------

    def buy_train(self, ttype, model):
        d = TRAIN_MODELS[ttype][model]
        if self.money < d["cost"] or self.points < d["unlock_pts"]:
            return None
        self.money -= d["cost"]
        tr = Train(ttype, model)
        self.all_trains.append(tr)
        self.unassigned.append(tr)
        return tr

    def can_buy(self, ttype, model):
        d = TRAIN_MODELS[ttype][model]
        return self.money >= d["cost"] and self.points >= d["unlock_pts"]

    def is_unlocked(self, ttype, model):
        return self.points >= TRAIN_MODELS[ttype][model]["unlock_pts"]

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN GUI
# ═══════════════════════════════════════════════════════════════════════════════

class MetroTycoonGUI:

    # ─── SETUP ──────────────────────────────────────────────────────────────

    def __init__(self, root):
        self.root = root
        root.title("Metro Tycoon")
        root.geometry(f"{WIN_W}x{WIN_H}")
        root.resizable(False, False)
        root.configure(bg="#000")

        self.cv = tk.Canvas(root, width=WIN_W, height=WIN_H,
                            bg=C_MAP_BG, highlightthickness=0)
        self.cv.pack()

        self.f_title = tkfont.Font(family="Segoe UI", size=34, weight="bold")
        self.f_big   = tkfont.Font(family="Segoe UI", size=17, weight="bold")
        self.f_med   = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_sm    = tkfont.Font(family="Segoe UI", size=9)
        self.f_xs    = tkfont.Font(family="Segoe UI", size=8)
        self.f_hud   = tkfont.Font(family="Consolas", size=11, weight="bold")

        self.game        = None
        self.state       = "title"     # title / playing / game_over
        self.panel_mode  = "lines"     # lines / shop / trains
        self.dragging    = False
        self.drag_line   = None        # existing line being extended
        self.drag_end    = "tail"      # which end: "head" or "tail"
        self.drag_sts    = []          # stations collected during drag
        self.assign_line = None
        self.hover_st    = None
        self.hover_x     = 0
        self.hover_y     = 0
        self.regions     = []          # click-regions
        self.sel_line    = None
        self.speed_mult  = 1
        self.last_t      = time.time()
        self.anim_t      = 0.0
        self.shop_scroll = 0

        self.cv.bind("<ButtonPress-1>",   self._press)
        self.cv.bind("<ButtonRelease-1>", self._release)
        self.cv.bind("<B1-Motion>",       self._drag)
        self.cv.bind("<Button-3>",        self._rclick)
        self.cv.bind("<Motion>",          self._motion)
        root.bind("<Escape>",             self._esc)
        root.bind("<space>",              self._space)

        self._loop()

    # ─── LOOP ───────────────────────────────────────────────────────────────

    def _loop(self):
        now = time.time()
        dt  = min(now - self.last_t, 0.1)
        self.last_t = now
        self.anim_t += dt

        if self.state == "playing" and self.game:
            self.game.update(dt * self.speed_mult)
            if self.game.game_over:
                self.state = "game_over"

        self._render()
        self.root.after(1000 // FPS, self._loop)

    # ─── RENDER ROUTER ─────────────────────────────────────────────────────

    def _render(self):
        self.cv.delete("all")
        self.regions.clear()
        if   self.state == "title":     self._r_title()
        elif self.state == "playing":   self._r_game()
        elif self.state == "game_over": self._r_over()

    # ─── TITLE ──────────────────────────────────────────────────────────────

    def _r_title(self):
        c = self.cv
        c.create_rectangle(0, 0, WIN_W, WIN_H, fill="#1a1a2e", outline="")

        # decorative lines
        for i in range(5):
            y   = 200 + i * 80
            col = LINE_COLORS[i]
            off = math.sin(self.anim_t * 0.5 + i * 0.7) * 30
            c.create_line(50+off, y, 400+off*2, y, fill=col, width=6, capstyle="round")
            c.create_oval(400+off*2-8, y-8, 400+off*2+8, y+8,
                          fill="#fff", outline=col, width=2)

        c.create_text(WIN_W//2, 140, text="METRO TYCOON",
                      font=self.f_title, fill="#fff")
        c.create_text(WIN_W//2, 190, text="A Transit Puzzle Game",
                      font=self.f_med, fill="#8888bb")

        info = [
            ("COMMUTER",   C_COMMUTER,  "Affordable & reliable short-distance trains"),
            ("INTERCITY",  C_INTERCITY, "Balanced speed & capacity for medium routes"),
            ("HIGH SPEED", C_HIGHSPEED, "Premium fast trains for your main lines"),
        ]
        for i, (nm, col, desc) in enumerate(info):
            y = 280 + i * 65
            c.create_rectangle(WIN_W//2-250, y-20, WIN_W//2+250, y+25,
                               fill="#0f0f2a", outline=col, width=2)
            c.create_text(WIN_W//2, y-4, text=nm, font=self.f_med, fill=col)
            c.create_text(WIN_W//2, y+15, text=desc, font=self.f_xs, fill="#8888aa")

        tips = [
            "Drag between stations to build metro lines",
            "Buy & assign trains to move passengers",
            "Earn points to unlock better train models",
            "Don't let any station overflow!",
        ]
        for i, t in enumerate(tips):
            c.create_text(WIN_W//2, 510+i*22, text=f"\u2022 {t}",
                          font=self.f_sm, fill="#9999bb")

        # start button
        bx, by, bw, bh = WIN_W//2-100, 630, 200, 50
        glow = 0.7 + 0.3 * abs(math.sin(self.anim_t * 2))
        gc   = "#%02x%02x%02x" % (int(46*glow), int(204*glow), int(113*glow))
        c.create_rectangle(bx, by, bx+bw, by+bh,
                           fill="#1a5276", outline=gc, width=2)
        c.create_text(bx+bw//2, by+bh//2, text="START GAME",
                      font=self.f_big, fill=gc)
        self.regions.append((bx, by, bw, bh, self._start))

    # ─── GAME OVER ─────────────────────────────────────────────────────────

    def _r_over(self):
        self._r_play_bg()
        c = self.cv
        c.create_rectangle(0, 0, WIN_W, WIN_H, fill="#000000", stipple="gray50")

        px, py, pw, ph = WIN_W//2-210, WIN_H//2-200, 420, 400
        c.create_rectangle(px, py, px+pw, py+ph,
                           fill="#1a1a2e", outline="#e63946", width=3)
        c.create_text(px+pw//2, py+35, text="GAME OVER",
                      font=self.f_title, fill="#e63946")
        c.create_text(px+pw//2, py+75, text=self.game.over_reason,
                      font=self.f_sm, fill="#ff8888")

        g = self.game
        mins = int(g.elapsed // 60); secs = int(g.elapsed % 60)
        stats = [
            f"Score: {g.score}",
            f"Passengers Delivered: {g.delivered}",
            f"Points Earned: {g.points}",
            f"Time: {mins}:{secs:02d}",
            f"Lines Built: {len(g.lines)}",
            f"Trains Owned: {len(g.all_trains)}",
        ]
        for i, s in enumerate(stats):
            c.create_text(px+pw//2, py+115+i*26, text=s,
                          font=self.f_sm, fill="#ccccee")

        bx, by, bw, bh = px+50, py+ph-65, 130, 40
        c.create_rectangle(bx, by, bx+bw, by+bh, fill="#1a5276", outline="#2ecc71", width=2)
        c.create_text(bx+bw//2, by+bh//2, text="PLAY AGAIN", font=self.f_med, fill="#2ecc71")
        self.regions.append((bx, by, bw, bh, self._start))

        bx2 = px+pw-180
        c.create_rectangle(bx2, by, bx2+bw, by+bh, fill="#1a5276", outline="#e63946", width=2)
        c.create_text(bx2+bw//2, by+bh//2, text="QUIT", font=self.f_med, fill="#e63946")
        self.regions.append((bx2, by, bw, bh, self.root.destroy))

    # ─── MAIN GAME RENDER ──────────────────────────────────────────────────

    def _r_game(self):
        self._r_play_bg()
        g = self.game
        if g.paused:
            c = self.cv
            c.create_rectangle(0, HUD_H, MAP_W, WIN_H, fill="#000000", stipple="gray50")
            c.create_text(MAP_W//2, WIN_H//2-10, text="PAUSED",
                          font=self.f_title, fill="#ffffff")
            c.create_text(MAP_W//2, WIN_H//2+35, text="Press SPACE to resume",
                          font=self.f_sm, fill="#aaaacc")

    def _r_play_bg(self):
        c = self.cv; g = self.game
        c.create_rectangle(0, HUD_H, MAP_W, WIN_H, fill=C_MAP_BG, outline="")
        self._draw_river()
        for ln in g.lines:
            self._draw_line(ln)
        if self.dragging and self.drag_sts:
            self._draw_preview()
        for st in g.stations:
            self._draw_station(st)
        for tr in g.all_trains:
            if tr.line:
                self._draw_train(tr)
        self._draw_hud()
        self._draw_panel()

    # ─── MAP ELEMENTS ──────────────────────────────────────────────────────

    def _draw_river(self):
        c = self.cv
        pts = []
        for i in range(25):
            t = i / 24
            x = MAP_W * 0.15 + MAP_W * 0.7 * t
            y = MAP_Y + MAP_H * 0.38 + math.sin(t * math.pi * 1.6 + 0.5) * 65
            pts += [x, y]
        if len(pts) >= 4:
            c.create_line(pts, fill=C_RIVER_EDGE, width=38, smooth=True, capstyle="round")
            c.create_line(pts, fill=C_RIVER,      width=28, smooth=True, capstyle="round")

    def _draw_line(self, ln):
        c = self.cv
        if not ln.stations:
            return
        idx = self.game.lines.index(ln) if ln in self.game.lines else 0
        nlines = max(1, len(self.game.lines))
        off = (idx - nlines / 2) * 4

        # draw segments
        for i in range(len(ln.stations) - 1):
            s1, s2 = ln.stations[i], ln.stations[i + 1]
            dx, dy = s2.x - s1.x, s2.y - s1.y
            d = max(1, math.hypot(dx, dy))
            nx, ny = -dy / d, dx / d
            c.create_line(s1.x + nx * off, s1.y + ny * off,
                          s2.x + nx * off, s2.y + ny * off,
                          fill=ln.color, width=5, capstyle="round")

        # station dots on line
        for st in ln.stations:
            c.create_oval(st.x - 5, st.y - 5, st.x + 5, st.y + 5,
                          fill=ln.color, outline="")

        # T-terminus markers at first and last station
        if len(ln.stations) >= 2:
            for end_idx, next_idx in [(0, 1), (-1, -2)]:
                ep  = ln.stations[end_idx]
                np_ = ln.stations[next_idx]
                dx, dy = np_.x - ep.x, np_.y - ep.y
                d = max(1, math.hypot(dx, dy))
                # direction pointing outward from the line
                tx, ty = -dx / d, -dy / d
                # perpendicular
                px, py = -ty, tx
                # T-bar position (just beyond the station edge)
                arm = STATION_SZ + 8
                bx = ep.x + tx * arm
                by = ep.y + ty * arm
                tlen = 10
                # stem from station edge to bar
                c.create_line(ep.x + tx * (STATION_SZ - 2),
                              ep.y + ty * (STATION_SZ - 2),
                              bx, by,
                              fill=ln.color, width=4, capstyle="round")
                # cross-bar
                c.create_line(bx - px * tlen, by - py * tlen,
                              bx + px * tlen, by + py * tlen,
                              fill=ln.color, width=4, capstyle="round")

    def _draw_preview(self):
        c = self.cv
        if self.drag_line:
            col = self.drag_line.color
        else:
            ci = -1
            for i in range(MAX_LINES):
                if i not in self.game.used_colors:
                    ci = i; break
            if ci == -1:
                return
            col = LINE_COLORS[ci]
        sts = self.drag_sts
        for i in range(len(sts) - 1):
            a, b = sts[i], sts[i + 1]
            c.create_line(a.x, a.y, b.x, b.y, fill=col, width=5,
                          dash=(10, 5), capstyle="round")
        last = sts[-1]
        if self.hover_x < MAP_W:
            c.create_line(last.x, last.y, self.hover_x, self.hover_y,
                          fill=col, width=3, dash=(6, 4), capstyle="round")
        # highlight snap target
        if self.hover_st and self.hover_st != last and self.hover_st not in sts:
            hx, hy = self.hover_st.x, self.hover_st.y
            c.create_oval(hx - STATION_SZ - 6, hy - STATION_SZ - 6,
                          hx + STATION_SZ + 6, hy + STATION_SZ + 6,
                          fill="", outline=col, width=3, dash=(4, 3))

    def _draw_station(self, st):
        c = self.cv; x, y = st.x, st.y; sz = STATION_SZ
        # overflow glow
        if len(st.passengers) > st.capacity:
            g = abs(math.sin(st.pulse)) * 0.8 + 0.2
            gsz = sz + 8 + math.sin(st.pulse) * 3
            c.create_oval(x-gsz, y-gsz, x+gsz, y+gsz,
                          fill="", outline=C_ST_CRIT, width=3)
        elif len(st.passengers) > st.capacity * 0.7:
            c.create_oval(x-sz-5, y-sz-5, x+sz+5, y+sz+5,
                          fill="", outline=C_ST_WARN, width=2)

        fill, out = C_ST_FILL, C_ST_LINE
        if st == self.hover_st:
            fill, out = "#e0e0ff", "#4444ff"

        draw_shape(c, st.shape, x, y, sz, fill=fill, outline=out, width=2.5)

        # passengers
        pax = st.passengers
        per = 7
        for i, p in enumerate(pax):
            col_ = i % per; row_ = i // per
            n_in_row = min(len(pax) - row_ * per, per)
            px = x - (n_in_row * 9) / 2 + col_ * 9 + 4
            py = y + sz + 10 + row_ * 11
            draw_shape(c, p.desired_shape, px, py, PAX_SZ,
                       fill=SHAPE_COLORS.get(p.desired_shape,"#888"), outline="")

        # overflow bar
        if st.overflow_t > 0:
            bw, bh = 38, 4
            pct = st.overflow_t / OVERFLOW_LIMIT
            bx_ = x - bw/2; by_ = y - sz - 12
            c.create_rectangle(bx_, by_, bx_+bw, by_+bh, fill="#333", outline="")
            c.create_rectangle(bx_, by_, bx_+bw*pct, by_+bh, fill=C_ST_CRIT, outline="")

    def _draw_train(self, tr):
        c = self.cv; x, y = tr.x, tr.y
        if tr.line is None:
            return
        col = tr.line.color
        # angle
        angle = 0
        ln = tr.line
        if len(ln.stations) >= 2:
            sg = max(0, min(tr.seg, len(ln.stations)-2))
            s1, s2 = ln.stations[sg], ln.stations[sg+1]
            angle = math.atan2(s2.y-s1.y, s2.x-s1.x)
            if tr.dir == -1:
                angle += math.pi

        # size by type
        ws = {"commuter": 12, "intercity": 16, "highspeed": 20}
        hs = {"commuter": 7,  "intercity": 8,  "highspeed": 7}
        w = ws.get(tr.ttype, 14); h = hs.get(tr.ttype, 8)

        ca, sa = math.cos(angle), math.sin(angle)
        corners = [
            (x + ca*w/2 - sa*h/2, y + sa*w/2 + ca*h/2),
            (x + ca*w/2 + sa*h/2, y + sa*w/2 - ca*h/2),
            (x - ca*w/2 + sa*h/2, y - sa*w/2 - ca*h/2),
            (x - ca*w/2 - sa*h/2, y - sa*w/2 + ca*h/2),
        ]
        # high-speed nose
        if tr.ttype == "highspeed":
            nose = (x + ca*(w/2+5), y + sa*(w/2+5))
            corners = [corners[0], nose, corners[1], corners[2], corners[3]]

        pts = [co for p in corners for co in p]
        c.create_polygon(pts, fill=col, outline="#222", width=1)

        # type dot
        tc = TYPE_COLORS[tr.ttype]
        c.create_oval(x-3, y-3, x+3, y+3, fill=tc, outline="")

        # pax count
        if tr.passengers:
            fc = "#fff" if len(tr.passengers) < tr.capacity else "#ffdd00"
            c.create_text(x, y-h-5, text=f"{len(tr.passengers)}/{tr.capacity}",
                          font=self.f_xs, fill=fc)

    # ─── HUD ───────────────────────────────────────────────────────────────

    def _draw_hud(self):
        c = self.cv; g = self.game
        c.create_rectangle(0, 0, WIN_W, HUD_H, fill=C_HUD_BG, outline="")
        c.create_line(0, HUD_H, WIN_W, HUD_H, fill="#333355")

        c.create_text(15,  HUD_H//2, text=f"Score: {g.score}",        font=self.f_hud, fill=C_SCORE, anchor="w")
        c.create_text(190, HUD_H//2, text=f"${g.money}",              font=self.f_hud, fill=C_GOLD,  anchor="w")
        c.create_text(310, HUD_H//2, text=f"Pts: {g.points}",         font=self.f_hud, fill="#bb88ff", anchor="w")
        c.create_text(470, HUD_H//2, text=f"Delivered: {g.delivered}", font=self.f_hud, fill="#88bbff", anchor="w")

        m = int(g.elapsed//60); s = int(g.elapsed%60)
        c.create_text(670, HUD_H//2, text=f"{m}:{s:02d}", font=self.f_hud, fill=C_HUD_TEXT, anchor="w")

        # speed button
        bx, by, bw, bh = MAP_W-125, 8, 50, HUD_H-16
        c.create_rectangle(bx, by, bx+bw, by+bh, fill=C_PANEL_BTN, outline="#555577")
        c.create_text(bx+bw//2, by+bh//2, text=f"{self.speed_mult}x",
                      font=self.f_sm, fill=C_HUD_TEXT)
        self.regions.append((bx, by, bw, bh, self._tog_speed))

        # pause button
        bx2 = MAP_W-65
        c.create_rectangle(bx2, by, bx2+bw, by+bh, fill=C_PANEL_BTN, outline="#555577")
        pt = "\u23f8" if not g.paused else "\u25b6"
        c.create_text(bx2+bw//2, by+bh//2, text=pt, font=self.f_sm, fill=C_HUD_TEXT)
        self.regions.append((bx2, by, bw, bh, self._tog_pause))

    # ─── PANEL ─────────────────────────────────────────────────────────────

    def _draw_panel(self):
        c = self.cv
        c.create_rectangle(PANEL_X, 0, WIN_W, WIN_H, fill=C_PANEL_BG, outline="")
        c.create_line(PANEL_X, 0, PANEL_X, WIN_H, fill="#333366", width=2)

        tw = PANEL_W // 3
        tabs = [("LINES","lines"), ("SHOP","shop"), ("TRAINS","trains")]
        for i, (lbl, md) in enumerate(tabs):
            tx = PANEL_X + i*tw
            act = self.panel_mode == md
            c.create_rectangle(tx, 0, tx+tw, HUD_H,
                               fill="#1a3355" if act else "#0d1b30", outline="#333366")
            c.create_text(tx+tw//2, HUD_H//2, text=lbl,
                          font=self.f_sm, fill="#fff" if act else "#6677aa")
            self.regions.append((tx, 0, tw, HUD_H,
                                 lambda m=md: self._set_pmode(m)))
        c.create_line(PANEL_X, HUD_H, WIN_W, HUD_H, fill=C_PANEL_SEP)

        y = HUD_H + 8
        if   self.panel_mode == "lines":  self._p_lines(y)
        elif self.panel_mode == "shop":   self._p_shop(y)
        elif self.panel_mode == "trains": self._p_trains(y)

    # ---- panel: LINES ---------------------------------------------------

    def _p_lines(self, y):
        c = self.cv; g = self.game

        # drag banner
        if self.dragging:
            action = "EXTENDING LINE" if self.drag_line else "BUILDING NEW LINE"
            col_b  = self.drag_line.color if self.drag_line else "#2ecc71"
            c.create_rectangle(PANEL_X+8, y, WIN_W-8, y+40,
                               fill="#1a3322", outline=col_b)
            c.create_text(PANEL_X+PANEL_W//2, y+10, text=action,
                          font=self.f_sm, fill=col_b)
            c.create_text(PANEL_X+PANEL_W//2, y+28,
                          text=f"Drag to stations \u2022 {len(self.drag_sts)} connected",
                          font=self.f_xs, fill="#88bb88")
            y += 48

        c.create_text(PANEL_X+12, y, text=f"Metro Lines ({len(g.lines)}/{MAX_LINES})",
                      font=self.f_med, fill=C_PANEL_BRIGHT, anchor="w")
        y += 22

        for ln in g.lines:
            sel = ln == self.sel_line
            lh = 25 + max(len(ln.trains), 1) * 16 + 24
            bg = "#1a2a4a" if sel else C_PANEL_SEC
            c.create_rectangle(PANEL_X+6, y, WIN_W-6, y+lh,
                               fill=bg, outline=ln.color if sel else "#2a3a5a")
            # name
            c.create_rectangle(PANEL_X+12, y+5, PANEL_X+26, y+19,
                               fill=ln.color, outline="")
            c.create_text(PANEL_X+32, y+12,
                          text=f"{ln.name} Line  ({len(ln.stations)} sta)",
                          font=self.f_sm, fill=C_PANEL_TEXT, anchor="w")
            self.regions.append((PANEL_X+6, y, PANEL_W-12, 22,
                                 lambda l=ln: self._sel_line(l)))

            ty = y + 24
            if ln.trains:
                for tr in ln.trains:
                    tc = TYPE_COLORS[tr.ttype]
                    c.create_oval(PANEL_X+18, ty+1, PANEL_X+26, ty+9, fill=tc, outline="")
                    c.create_text(PANEL_X+32, ty+5,
                                  text=f"{tr.model} ({len(tr.passengers)}/{tr.capacity})",
                                  font=self.f_xs, fill=C_PANEL_DIM, anchor="w")
                    ty += 16
            else:
                c.create_text(PANEL_X+32, ty+5, text="(no trains)",
                              font=self.f_xs, fill="#555577", anchor="w")
                ty += 16

            abx = PANEL_X+12; abw = PANEL_W-24
            c.create_rectangle(abx, ty, abx+abw, ty+20,
                               fill="#0a2040", outline="#446688")
            c.create_text(abx+abw//2, ty+10, text="+ Add Train",
                          font=self.f_xs, fill="#6699cc")
            self.regions.append((abx, ty, abw, 20,
                                 lambda l=ln: self._start_assign(l)))
            y += lh + 5

        # selected line actions
        if self.sel_line and not self.dragging:
            bw2 = (PANEL_W - 30) // 2; bh2 = 26
            bx1 = PANEL_X + 8
            bx2 = PANEL_X + 16 + bw2
            # drag hint
            c.create_text(PANEL_X+12, y,
                          text="Drag from a T-end to extend this line",
                          font=self.f_xs, fill="#6699aa", anchor="w")
            y += 18
            # remove last
            c.create_rectangle(bx1, y, bx1+bw2, y+bh2,
                               fill="#2a2a1a", outline="#aa8833")
            c.create_text(bx1+bw2//2, y+bh2//2, text="Remove Last Sta",
                          font=self.f_xs, fill="#ddaa44")
            self.regions.append((bx1, y, bw2, bh2, self._remove_last_st))
            # delete line
            c.create_rectangle(bx2, y, bx2+bw2, y+bh2,
                               fill="#3a1a1a", outline="#e63946")
            c.create_text(bx2+bw2//2, y+bh2//2, text="Delete Line",
                          font=self.f_xs, fill="#ee6666")
            self.regions.append((bx2, y, bw2, bh2, self._del_sel_line))
            y += 34

        # drag instructions
        if not self.dragging:
            c.create_rectangle(PANEL_X+8, y, WIN_W-8, y+38,
                               fill="#0d1b30", outline="#2a3f6f")
            if g.lines:
                tip = "Drag from a T-end to extend a line"
            else:
                tip = "Drag from a station to create a line"
            c.create_text(PANEL_X+PANEL_W//2, y+12, text=tip,
                          font=self.f_xs, fill="#6699aa")
            c.create_text(PANEL_X+PANEL_W//2, y+28,
                          text="Or drag from any station for a new line",
                          font=self.f_xs, fill="#4477aa")
            y += 44

        # unassigned
        if g.unassigned:
            c.create_text(PANEL_X+12, y,
                          text=f"Unassigned trains: {len(g.unassigned)}",
                          font=self.f_xs, fill=C_ST_WARN, anchor="w")

    # ---- panel: SHOP ----------------------------------------------------

    def _p_shop(self, y):
        c = self.cv; g = self.game
        c.create_text(PANEL_X+12, y, text="TRAIN SHOP",
                      font=self.f_med, fill=C_PANEL_BRIGHT, anchor="w")
        c.create_text(WIN_W-12, y, text=f"${g.money}",
                      font=self.f_med, fill=C_GOLD, anchor="e")
        y += 22

        if self.assign_line:
            c.create_rectangle(PANEL_X+8, y, WIN_W-8, y+22,
                               fill="#1a3322", outline="#2ecc71")
            c.create_text(PANEL_X+PANEL_W//2, y+11,
                          text=f"Buy \u2192 assign to {self.assign_line.name} Line",
                          font=self.f_xs, fill="#2ecc71")
            y += 26

        for ttype in ("commuter", "intercity", "highspeed"):
            tc = TYPE_COLORS[ttype]; lab = TYPE_LABELS[ttype]
            c.create_rectangle(PANEL_X+6, y, WIN_W-6, y+20,
                               fill=tc, outline="")
            c.create_text(PANEL_X+PANEL_W//2, y+10, text=lab.upper(),
                          font=self.f_sm, fill="#fff")
            y += 24

            for mn, d in TRAIN_MODELS[ttype].items():
                unlk  = g.is_unlocked(ttype, mn)
                canb  = g.can_buy(ttype, mn)
                rbg   = "#0d1b30" if unlk else "#0a0a1a"
                c.create_rectangle(PANEL_X+6, y, WIN_W-6, y+44,
                                   fill=rbg, outline="#1a2a4a")
                nc = C_PANEL_TEXT if unlk else C_LOCKED
                c.create_text(PANEL_X+14, y+10, text=mn,
                              font=self.f_sm, fill=nc, anchor="w")
                c.create_text(PANEL_X+14, y+26,
                              text=f"Spd {d['speed']}  Cap {d['capacity']}",
                              font=self.f_xs, fill=C_PANEL_DIM, anchor="w")
                if not unlk:
                    c.create_text(PANEL_X+14, y+38,
                                  text=f"\U0001f512 {d['unlock_pts']} pts to unlock",
                                  font=self.f_xs, fill=C_LOCKED, anchor="w")
                else:
                    ct = "FREE" if d["cost"] == 0 else f"${d['cost']}"
                    bbx = WIN_W-75; bbw = 60; bbh = 22; bby = y+11
                    if canb:
                        c.create_rectangle(bbx, bby, bbx+bbw, bby+bbh,
                                           fill="#1a5276", outline="#2ecc71")
                        c.create_text(bbx+bbw//2, bby+bbh//2, text=ct,
                                      font=self.f_xs, fill="#2ecc71")
                        self.regions.append((bbx, bby, bbw, bbh,
                                             lambda tt=ttype, m=mn: self._do_buy(tt, m)))
                    else:
                        c.create_rectangle(bbx, bby, bbx+bbw, bby+bbh,
                                           fill="#1a1a2a", outline="#444455")
                        c.create_text(bbx+bbw//2, bby+bbh//2, text=ct,
                                      font=self.f_xs, fill="#666")
                y += 48
            y += 2

    # ---- panel: TRAINS ---------------------------------------------------

    def _p_trains(self, y):
        c = self.cv; g = self.game

        if self.assign_line:
            ln = self.assign_line
            c.create_rectangle(PANEL_X+6, y, WIN_W-6, y+30,
                               fill="#1a3322", outline="#2ecc71")
            c.create_text(PANEL_X+PANEL_W//2, y+10,
                          text=f"ASSIGN TO: {ln.name} Line",
                          font=self.f_sm, fill="#2ecc71")
            c.create_text(PANEL_X+PANEL_W//2, y+24,
                          text="Select a train below  (or buy from Shop)",
                          font=self.f_xs, fill="#88bb88")
            y += 36
            bx, bw = PANEL_X+10, PANEL_W-20
            c.create_rectangle(bx, y, bx+bw, y+20,
                               fill="#3a1a1a", outline="#e63946")
            c.create_text(bx+bw//2, y+10, text="Cancel",
                          font=self.f_xs, fill="#e63946")
            self.regions.append((bx, y, bw, 20, self._cancel_assign))
            y += 28

        c.create_text(PANEL_X+12, y, text="YOUR TRAINS",
                      font=self.f_med, fill=C_PANEL_BRIGHT, anchor="w")
        y += 18
        c.create_text(PANEL_X+12, y,
                      text=f"Total: {len(g.all_trains)}    Unassigned: {len(g.unassigned)}",
                      font=self.f_xs, fill=C_PANEL_DIM, anchor="w")
        y += 18

        for ttype in ("commuter", "intercity", "highspeed"):
            trains = [t for t in g.all_trains if t.ttype == ttype]
            if not trains:
                continue
            tc  = TYPE_COLORS[ttype]
            lab = TYPE_LABELS[ttype]
            c.create_text(PANEL_X+12, y, text=f"{lab} ({len(trains)})",
                          font=self.f_sm, fill=tc, anchor="w")
            y += 18
            for tr in trains:
                asgn = tr.line is not None
                bg   = "#0d1b30" if asgn else "#1a1a22"
                c.create_rectangle(PANEL_X+8, y, WIN_W-8, y+36,
                                   fill=bg, outline="#1a2a4a")
                c.create_text(PANEL_X+16, y+9, text=tr.model,
                              font=self.f_xs, fill=C_PANEL_TEXT, anchor="w")
                if asgn:
                    c.create_text(PANEL_X+16, y+24,
                                  text=f"On {tr.line.name} Line  ({len(tr.passengers)}/{tr.capacity})",
                                  font=self.f_xs, fill=tr.line.color, anchor="w")
                    ubx = WIN_W-65; ubw = 52
                    c.create_rectangle(ubx, y+4, ubx+ubw, y+32,
                                       fill="#2a1a1a", outline="#aa5555")
                    c.create_text(ubx+ubw//2, y+18, text="Remove",
                                  font=self.f_xs, fill="#ee6666")
                    self.regions.append((ubx, y+4, ubw, 28,
                                         lambda t=tr: self._unassign(t)))
                else:
                    c.create_text(PANEL_X+16, y+24, text="Unassigned",
                                  font=self.f_xs, fill=C_ST_WARN, anchor="w")
                    if self.assign_line:
                        abx = WIN_W-65; abw = 52
                        c.create_rectangle(abx, y+4, abx+abw, y+32,
                                           fill="#1a3322", outline="#2ecc71")
                        c.create_text(abx+abw//2, y+18, text="Assign",
                                      font=self.f_xs, fill="#2ecc71")
                        self.regions.append((abx, y+4, abw, 28,
                                             lambda t=tr: self._do_assign(t)))
                y += 40
            y += 4

    # ─── EVENT HANDLERS ────────────────────────────────────────────────────

    def _press(self, ev):
        mx, my = ev.x, ev.y
        # check panel / HUD buttons first
        for (rx, ry, rw, rh, cb) in reversed(self.regions):
            if rx <= mx <= rx + rw and ry <= my <= ry + rh:
                cb(); return
        # map press — start a drag
        if self.state == "playing" and mx < MAP_W and my > HUD_H and self.game:
            self._map_press(mx, my)

    def _release(self, ev):
        if self.dragging:
            self._finish_drag()

    def _drag(self, ev):
        self.hover_x, self.hover_y = ev.x, ev.y
        self._update_hover(ev.x, ev.y)
        if self.dragging and self.hover_st:
            self._try_add_drag_station(self.hover_st)

    def _rclick(self, ev):
        if self.dragging:
            self._cancel_drag()

    def _motion(self, ev):
        self.hover_x, self.hover_y = ev.x, ev.y
        self._update_hover(ev.x, ev.y)

    def _update_hover(self, mx, my):
        self.hover_st = None
        if self.state == "playing" and mx < MAP_W and self.game:
            for st in self.game.stations:
                if math.hypot(st.x - mx, st.y - my) < STATION_SZ + 10:
                    self.hover_st = st; break

    def _esc(self, _):
        if self.dragging:
            self._cancel_drag()
        elif self.assign_line:
            self._cancel_assign()
        elif self.game and self.game.paused:
            self.game.paused = False

    def _space(self, _):
        if self.state == "playing" and self.game:
            self.game.paused = not self.game.paused

    def _map_press(self, mx, my):
        g = self.game
        clicked = None
        for st in g.stations:
            if math.hypot(st.x - mx, st.y - my) < STATION_SZ + 10:
                clicked = st; break
        if not clicked:
            self.sel_line = None
            return

        # check if this station is a terminus of an existing line
        for ln in g.lines:
            if not ln.stations:
                continue
            if clicked == ln.stations[0]:
                self.dragging  = True
                self.drag_line = ln
                self.drag_end  = "head"
                self.drag_sts  = [clicked]
                self.sel_line  = ln
                return
            if clicked == ln.stations[-1]:
                self.dragging  = True
                self.drag_line = ln
                self.drag_end  = "tail"
                self.drag_sts  = [clicked]
                self.sel_line  = ln
                return

        # otherwise start a new line from this station
        if len(g.lines) < MAX_LINES:
            self.dragging  = True
            self.drag_line = None
            self.drag_end  = "tail"
            self.drag_sts  = [clicked]

    def _try_add_drag_station(self, st):
        """Add a station to the drag chain if valid."""
        if not self.drag_sts:
            return
        if st in self.drag_sts:
            return
        # don't re-add stations already in the line being extended
        if self.drag_line and st in self.drag_line.stations:
            return
        self.drag_sts.append(st)

    # ─── ACTIONS ───────────────────────────────────────────────────────────

    def _start(self):
        Station._nid = 0; MetroLine._nid = 0; Train._nid = 0
        self.game       = GameState()
        self.state       = "playing"
        self.panel_mode  = "lines"
        self.dragging    = False
        self.drag_line   = None
        self.drag_sts    = []
        self.assign_line = None
        self.sel_line    = None
        self.speed_mult  = 1
        self.last_t      = time.time()

    def _set_pmode(self, m):
        self.panel_mode = m
        if m != "trains":
            self.assign_line = None

    def _tog_speed(self):
        self.speed_mult = self.speed_mult % 3 + 1

    def _tog_pause(self):
        if self.game:
            self.game.paused = not self.game.paused

    # drag line building
    def _finish_drag(self):
        g = self.game
        new_sts = self.drag_sts[1:]   # first station is the anchor
        if self.drag_line and new_sts:
            # extend existing line
            if self.drag_end == "tail":
                for s in new_sts:
                    g.add_station_to_line(self.drag_line, s)
            else:  # head
                for s in reversed(new_sts):
                    if s not in self.drag_line.stations:
                        self.drag_line.stations.insert(0, s)
                g._reset_line_trains(self.drag_line)
            self.sel_line = self.drag_line
        elif self.drag_line and not new_sts:
            # just clicked a terminus — select its line
            self.sel_line = self.drag_line
        elif not self.drag_line and len(self.drag_sts) >= 2:
            # create new line
            ln = g.create_line(self.drag_sts)
            if ln:
                self.sel_line = ln
        self.dragging = False; self.drag_line = None; self.drag_sts = []

    def _cancel_drag(self):
        self.dragging = False; self.drag_line = None; self.drag_sts = []

    def _sel_line(self, ln):
        self.sel_line = None if self.sel_line == ln else ln

    def _del_sel_line(self):
        if self.sel_line:
            self.game.delete_line(self.sel_line)
            self.sel_line = None

    def _remove_last_st(self):
        if self.sel_line:
            self.game.remove_last_station(self.sel_line)

    # trains / assignment
    def _start_assign(self, ln):
        self.assign_line = ln
        self.panel_mode  = "shop"

    def _cancel_assign(self):
        self.assign_line = None
        self.panel_mode  = "lines"

    def _do_assign(self, tr):
        if self.assign_line:
            self.game.assign_train(tr, self.assign_line)
            self.assign_line = None
            self.panel_mode  = "lines"

    def _unassign(self, tr):
        self.game.unassign_train(tr)

    def _do_buy(self, ttype, model):
        tr = self.game.buy_train(ttype, model)
        if tr and self.assign_line:
            self.game.assign_train(tr, self.assign_line)
            self.assign_line = None
            self.panel_mode  = "lines"

# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    MetroTycoonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
