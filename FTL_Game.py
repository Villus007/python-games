"""
FTL Lite — A Simplified 'Faster Than Light' Roguelike
======================================================
Navigate your ship through 5 sectors, manage crew and systems,
fight hostile ships, visit stores, and defeat the Rebel Flagship!

Controls: Type the number/letter of your choice and press Enter.
"""

import random
import os
import time
import sys

# Fix Windows console encoding for Unicode box-drawing characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    os.system("chcp 65001 >nul 2>&1")

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

SECTOR_COUNT = 5
BEACONS_PER_SECTOR = 6
STARTING_FUEL = 16
STARTING_MISSILES = 8
STARTING_SCRAP = 30

# ─── HELPER UTILITIES ────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="Press Enter to continue..."):
    input(f"\n{msg}")

def banner(text, char="═", width=60):
    print(f"\n{char * width}")
    print(f"{text:^{width}}")
    print(f"{char * width}")

def colored(text, code):
    """ANSI colored text (works in most modern terminals)."""
    return f"\033[{code}m{text}\033[0m"

def red(t):    return colored(t, "91")
def green(t):  return colored(t, "92")
def yellow(t): return colored(t, "93")
def cyan(t):   return colored(t, "96")
def bold(t):   return colored(t, "1")

# ─── DATA: CREW SPECIES ──────────────────────────────────────────────────────

SPECIES = {
    "Human":  {"hp": 100, "combat": 10, "repair": 10, "special": "Versatile (no weaknesses)"},
    "Engi":   {"hp":  80, "combat":  5, "repair": 20, "special": "Expert repairs, weak in combat"},
    "Mantis": {"hp": 100, "combat": 20, "repair":  5, "special": "Fierce fighters, poor repairs"},
    "Rock":   {"hp": 150, "combat": 12, "repair":  8, "special": "Fire immune, very tough"},
    "Zoltan": {"hp":  70, "combat":  8, "repair": 10, "special": "+1 bonus power to systems"},
}

# ─── DATA: WEAPONS ────────────────────────────────────────────────────────────

WEAPONS = {
    "Burst Laser I":    {"damage": 2, "shield_pierce": 1, "uses_missiles": False, "cost": 40,  "power": 1},
    "Burst Laser II":   {"damage": 3, "shield_pierce": 1, "uses_missiles": False, "cost": 80,  "power": 2},
    "Heavy Laser":      {"damage": 4, "shield_pierce": 2, "uses_missiles": False, "cost": 65,  "power": 2},
    "Artemis Missile":  {"damage": 3, "shield_pierce": 99, "uses_missiles": True, "cost": 30,  "power": 1},
    "Hermes Missile":   {"damage": 4, "shield_pierce": 99, "uses_missiles": True, "cost": 55,  "power": 2},
    "Ion Blast":        {"damage": 1, "shield_pierce": 3, "uses_missiles": False, "cost": 50,  "power": 1},
    "Pike Beam":        {"damage": 3, "shield_pierce": 0, "uses_missiles": False, "cost": 60,  "power": 2},
    "Hull Laser":       {"damage": 3, "shield_pierce": 2, "uses_missiles": False, "cost": 70,  "power": 2},
}

# ─── DATA: ENEMY SHIP TEMPLATES ──────────────────────────────────────────────

def make_enemy(sector):
    """Generate an enemy ship scaled to the current sector difficulty."""
    templates = [
        {"name": "Pirate Scout",    "hull_base": 8,  "shields_base": 0, "damage_base": 2, "evade": 15},
        {"name": "Rebel Fighter",   "hull_base": 12, "shields_base": 1, "damage_base": 3, "evade": 10},
        {"name": "Mantis Raider",   "hull_base": 10, "shields_base": 0, "damage_base": 4, "evade": 20},
        {"name": "Rock Cruiser",    "hull_base": 18, "shields_base": 2, "damage_base": 2, "evade": 5},
        {"name": "Slug Interceptor","hull_base": 10, "shields_base": 1, "damage_base": 3, "evade": 25},
        {"name": "Auto-Scout",      "hull_base": 8,  "shields_base": 1, "damage_base": 2, "evade": 30},
        {"name": "Engi Bomber",     "hull_base": 14, "shields_base": 1, "damage_base": 3, "evade": 10},
    ]
    t = random.choice(templates)
    scale = 1 + sector * 0.35
    return {
        "name": f"{t['name']} (Sector {sector + 1})",
        "hull": int(t["hull_base"] * scale),
        "max_hull": int(t["hull_base"] * scale),
        "shields": t["shields_base"] + sector // 2,
        "damage": int(t["damage_base"] * scale),
        "evade": t["evade"] + sector * 3,
        "reward_scrap": random.randint(10, 20) + sector * 8,
        "reward_fuel": random.randint(1, 3),
        "reward_missiles": random.randint(0, 2),
    }

def make_flagship():
    """The final Rebel Flagship — a tough multi-phase boss."""
    return {
        "name": "☠  REBEL FLAGSHIP  ☠",
        "hull": 50,
        "max_hull": 50,
        "shields": 4,
        "damage": 6,
        "evade": 20,
        "reward_scrap": 0,
        "reward_fuel": 0,
        "reward_missiles": 0,
        "phase": 1,
        "max_phase": 3,
    }

# ─── DATA: RANDOM EVENTS ─────────────────────────────────────────────────────

def get_event(sector, ship):
    """Return a random event dict: {text, choices: [{label, outcome_fn}]}."""
    events = []

    # — Distress Signal —
    def distress_help():
        if random.random() < 0.6:
            species = random.choice(list(SPECIES.keys()))
            ship["crew"].append(make_crew(species))
            return green(f"You rescued a {species} crew member! They join your ship.")
        else:
            dmg = random.randint(1, 3)
            ship["hull"] -= dmg
            return red(f"It was a trap! Your hull takes {dmg} damage.")

    def distress_ignore():
        return yellow("You fly past. Nothing happens.")

    events.append({
        "text": "You pick up a distress signal from a nearby moon.",
        "choices": [
            {"label": "Investigate the signal", "fn": distress_help},
            {"label": "Ignore it and move on",  "fn": distress_ignore},
        ]
    })

    # — Asteroid Field —
    def asteroid_brave():
        if random.random() < 0.5:
            scrap = random.randint(10, 25)
            ship["scrap"] += scrap
            return green(f"You navigate safely and salvage {scrap} scrap from debris!")
        else:
            dmg = random.randint(2, 5)
            ship["hull"] -= dmg
            return red(f"Asteroids batter your hull for {dmg} damage!")

    def asteroid_avoid():
        ship["fuel"] -= 1
        return yellow("You detour around. It costs 1 extra fuel.")

    events.append({
        "text": "An asteroid field blocks the most direct route.",
        "choices": [
            {"label": "Fly through carefully", "fn": asteroid_brave},
            {"label": "Take a detour (-1 fuel)", "fn": asteroid_avoid},
        ]
    })

    # — Derelict Ship —
    def derelict_board():
        r = random.random()
        if r < 0.4:
            scrap = random.randint(15, 35)
            ship["scrap"] += scrap
            return green(f"Your crew finds {scrap} scrap aboard the wreck!")
        elif r < 0.7:
            wname = random.choice(list(WEAPONS.keys()))
            ship["weapons"].append(wname)
            return green(f"You found a {wname} floating in the wreckage!")
        else:
            dmg = random.randint(2, 4)
            ship["hull"] -= dmg
            return red(f"A booby trap explodes! {dmg} hull damage.")

    def derelict_scan():
        scrap = random.randint(5, 12)
        ship["scrap"] += scrap
        return yellow(f"Long-range scans reveal minor salvage: {scrap} scrap.")

    events.append({
        "text": "A derelict ship drifts silently among the stars.",
        "choices": [
            {"label": "Send a boarding party", "fn": derelict_board},
            {"label": "Scan from a distance",  "fn": derelict_scan},
        ]
    })

    # — Merchant —
    def merchant_trade():
        if ship["scrap"] >= 15:
            ship["scrap"] -= 15
            ship["fuel"] += 5
            ship["missiles"] += 3
            return green("Traded 15 scrap for 5 fuel and 3 missiles.")
        return red("You don't have enough scrap (need 15).")

    def merchant_decline():
        return yellow("You decline and move on.")

    events.append({
        "text": "A traveling merchant hails you, offering supplies.",
        "choices": [
            {"label": "Trade 15 scrap for fuel & missiles", "fn": merchant_trade},
            {"label": "Decline",                             "fn": merchant_decline},
        ]
    })

    # — Nebula —
    def nebula_explore():
        if random.random() < 0.5:
            scrap = random.randint(8, 20)
            ship["scrap"] += scrap
            return green(f"Hidden within the nebula you find {scrap} scrap!")
        else:
            return yellow("The nebula is empty. You press on.")

    def nebula_skip():
        return yellow("You steer clear of the nebula.")

    events.append({
        "text": "A swirling nebula looms ahead, hiding what's inside.",
        "choices": [
            {"label": "Explore the nebula", "fn": nebula_explore},
            {"label": "Avoid it",           "fn": nebula_skip},
        ]
    })

    # — Crew Illness —
    def illness_treat():
        if ship["scrap"] >= 10:
            ship["scrap"] -= 10
            return green("You purchase medicine. The crew recovers fully!")
        else:
            if ship["crew"]:
                lost = ship["crew"].pop()
                return red(f"No scrap for medicine — {lost['name']} the {lost['species']} succumbs to the illness.")
            return red("No scrap and no crew to lose... things are dire.")

    def illness_ignore():
        if ship["crew"] and random.random() < 0.4:
            lost = ship["crew"].pop()
            return red(f"{lost['name']} the {lost['species']} couldn't fight off the sickness and has died.")
        return yellow("The crew toughs it out. Everyone survives... this time.")

    events.append({
        "text": "A strange illness sweeps through the ship!",
        "choices": [
            {"label": "Spend 10 scrap on medicine", "fn": illness_treat},
            {"label": "Hope they recover on their own", "fn": illness_ignore},
        ]
    })

    return random.choice(events)

# ─── CREW HELPERS ─────────────────────────────────────────────────────────────

_crew_names = [
    "Alex", "Brin", "Cael", "Dara", "Eris", "Finn", "Gael", "Hana",
    "Iris", "Jace", "Kira", "Lorn", "Mira", "Niko", "Orin", "Pax",
    "Quinn", "Reva", "Sven", "Tova", "Uma", "Vex", "Wren", "Xyla", "Yuri", "Zara"
]

def make_crew(species=None):
    if species is None:
        species = random.choice(list(SPECIES.keys()))
    stats = SPECIES[species]
    return {
        "name": random.choice(_crew_names),
        "species": species,
        "hp": stats["hp"],
        "max_hp": stats["hp"],
        "combat": stats["combat"],
        "repair": stats["repair"],
    }

# ─── SHIP ─────────────────────────────────────────────────────────────────────

def create_player_ship():
    return {
        "name": "The Kestrel",
        "hull": 30,
        "max_hull": 30,
        "shields": 1,          # shield layers (each blocks 1 damage)
        "engines": 1,          # each level = +5% evade
        "max_power": 8,
        "weapons": ["Burst Laser I", "Artemis Missile"],
        "crew": [make_crew("Human"), make_crew("Human"), make_crew("Engi")],
        "fuel": STARTING_FUEL,
        "missiles": STARTING_MISSILES,
        "scrap": STARTING_SCRAP,
    }

def ship_evade_chance(ship):
    engines = ship.get("engines", 1)
    base = engines * 5
    pilot_bonus = 5 if any(c["species"] == "Human" for c in ship["crew"]) else 0
    return min(base + pilot_bonus, 45)

# ─── DISPLAY ──────────────────────────────────────────────────────────────────

def show_ship_status(ship):
    hull_bar = bar(ship["hull"], ship["max_hull"], 20)
    crew_str = ", ".join(f"{c['name']}({c['species'][0]})" for c in ship["crew"])
    weapons_str = ", ".join(ship["weapons"]) if ship["weapons"] else "None"
    print(f"""
┌──────────────────── {bold(ship['name'])} ────────────────────┐
│  Hull:     {hull_bar} {ship['hull']}/{ship['max_hull']}
│  Shields:  {'█ ' * ship['shields']}(Level {ship['shields']})
│  Engines:  Level {ship.get('engines', 1)}  (Evade: {ship_evade_chance(ship)}%)
│  Weapons:  {weapons_str}
│  Crew:     {crew_str or 'NONE'}
│  Fuel: {ship['fuel']}  │  Missiles: {ship['missiles']}  │  Scrap: {ship['scrap']}
└───────────────────────────────────────────────────────┘""")

def bar(current, maximum, width=20):
    filled = int(width * max(current, 0) / max(maximum, 1))
    return green("█" * filled) + "░" * (width - filled)

def show_enemy_status(enemy):
    hull_bar = bar(enemy["hull"], enemy["max_hull"], 15)
    print(f"  {red(enemy['name'])}  Hull: {hull_bar} {enemy['hull']}/{enemy['max_hull']}  Shields: {enemy['shields']}  Evade: {enemy['evade']}%")

# ─── COMBAT ───────────────────────────────────────────────────────────────────

def combat(ship, enemy):
    """Turn-based combat. Returns True if player won, False if lost/fled."""
    banner(f"COMBAT: {enemy['name']}", "─")
    turn = 1

    while ship["hull"] > 0 and enemy["hull"] > 0:
        print(f"\n{'─'*50}")
        print(bold(f"  ── Turn {turn} ──"))
        show_ship_status(ship)
        show_enemy_status(enemy)

        # Player actions
        print(f"\n  Actions:")
        for i, wname in enumerate(ship["weapons"]):
            w = WEAPONS[wname]
            mflag = " [M]" if w["uses_missiles"] else ""
            print(f"    [{i+1}] Fire {wname} (dmg:{w['damage']} pierce:{w['shield_pierce']}){mflag}")
        print(f"    [R] Attempt to flee (engine check)")
        if ship["crew"]:
            print(f"    [H] Repair hull (+{sum(c['repair'] for c in ship['crew'])//5} HP, skip attack)")

        choice = input("\n  > ").strip().upper()

        # — Flee —
        if choice == "R":
            evade = ship_evade_chance(ship)
            if random.randint(1, 100) <= evade + 20:
                print(yellow("\n  Your engines spin up — you jump away!"))
                ship["fuel"] -= 1
                pause()
                return None  # fled
            else:
                print(red("\n  FTL drive charging... not fast enough!"))

        # — Repair —
        elif choice == "H" and ship["crew"]:
            repair_amt = max(1, sum(c["repair"] for c in ship["crew"]) // 5)
            ship["hull"] = min(ship["hull"] + repair_amt, ship["max_hull"])
            print(green(f"\n  Crew repairs {repair_amt} hull points."))

        # — Fire weapon —
        elif choice.isdigit() and 1 <= int(choice) <= len(ship["weapons"]):
            idx = int(choice) - 1
            wname = ship["weapons"][idx]
            w = WEAPONS[wname]

            if w["uses_missiles"]:
                if ship["missiles"] <= 0:
                    print(red("  No missiles left!"))
                    continue
                ship["missiles"] -= 1

            # Hit check
            if random.randint(1, 100) <= enemy["evade"]:
                print(yellow(f"\n  {wname} fires... MISS!"))
            else:
                effective_shields = max(0, enemy["shields"] - w["shield_pierce"])
                dmg = max(0, w["damage"] - effective_shields)
                enemy["hull"] -= dmg
                if dmg > 0:
                    print(green(f"\n  {wname} hits for {dmg} damage! (shields blocked {w['damage'] - dmg})"))
                else:
                    print(yellow(f"\n  {wname} hits but shields absorb all damage!"))
        else:
            print("  Invalid choice.")
            continue

        # — Enemy turn —
        if enemy["hull"] > 0:
            print()
            evade = ship_evade_chance(ship)
            if random.randint(1, 100) <= evade:
                print(cyan(f"  {enemy['name']} fires... your ship dodges!"))
            else:
                dmg = max(0, enemy["damage"] - ship["shields"])
                ship["hull"] -= dmg
                if dmg > 0:
                    print(red(f"  {enemy['name']} hits you for {dmg} damage!"))
                    # Random crew injury
                    if random.random() < 0.2 and ship["crew"]:
                        injured = random.choice(ship["crew"])
                        injury = random.randint(10, 25)
                        injured["hp"] -= injury
                        if injured["hp"] <= 0:
                            ship["crew"].remove(injured)
                            print(red(f"  {injured['name']} the {injured['species']} has been killed!"))
                        else:
                            print(yellow(f"  {injured['name']} takes {injury} injury ({injured['hp']} HP left)."))
                else:
                    print(cyan(f"  {enemy['name']} fires but your shields hold!"))

        turn += 1

    # Outcome
    if enemy["hull"] <= 0:
        print(green(f"\n  ✓ {enemy['name']} destroyed!"))
        ship["scrap"] += enemy["reward_scrap"]
        ship["fuel"] += enemy["reward_fuel"]
        ship["missiles"] += enemy["reward_missiles"]
        print(f"  Rewards: +{enemy['reward_scrap']} scrap, +{enemy['reward_fuel']} fuel, +{enemy['reward_missiles']} missiles")
        pause()
        return True
    else:
        return False  # player destroyed

# ─── FLAGSHIP COMBAT (multi-phase) ───────────────────────────────────────────

def flagship_combat(ship):
    """Three-phase fight against the Rebel Flagship."""
    flagship = make_flagship()
    for phase in range(1, 4):
        flagship["phase"] = phase
        flagship["hull"] = 30 + phase * 10
        flagship["max_hull"] = flagship["hull"]
        flagship["shields"] = 2 + phase
        flagship["damage"] = 4 + phase * 2
        flagship["evade"] = 15 + phase * 5
        flagship["reward_scrap"] = 0
        flagship["reward_fuel"] = 0
        flagship["reward_missiles"] = 0

        banner(f"FLAGSHIP PHASE {phase}/3", "█")
        print(f"  The Flagship reconfigures! Phase {phase} begins.")
        if phase == 2:
            print(yellow("  Boarding drones launch! A random crew member takes damage."))
            if ship["crew"]:
                victim = random.choice(ship["crew"])
                victim["hp"] -= 30
                if victim["hp"] <= 0:
                    ship["crew"].remove(victim)
                    print(red(f"  {victim['name']} was overwhelmed by boarders and killed!"))
                else:
                    print(yellow(f"  {victim['name']} fights off boarders ({victim['hp']} HP left)."))
        elif phase == 3:
            print(yellow("  Power surge! Your shields are temporarily reduced by 1."))
            ship["shields"] = max(0, ship["shields"] - 1)

        pause("Press Enter to engage...")
        result = combat(ship, flagship)
        if result is None:
            print(red("  You cannot flee the Flagship!"))
            ship["hull"] -= flagship["damage"]
            if ship["hull"] <= 0:
                return False
            continue
        if not result:
            return False

        if phase < 3:
            # Small heal between phases
            heal = 5
            ship["hull"] = min(ship["hull"] + heal, ship["max_hull"])
            print(green(f"\n  Between phases you patch {heal} hull."))
            pause()

    return True  # Victory!

# ─── STORE ────────────────────────────────────────────────────────────────────

def visit_store(ship):
    banner("STORE", "─")
    # Generate store inventory
    available_weapons = random.sample(list(WEAPONS.keys()), min(3, len(WEAPONS)))
    repair_cost = 2  # per hull point
    fuel_cost = 3
    missile_cost = 6
    shield_cost = 50 + ship["shields"] * 30
    engine_cost = 30 + ship.get("engines", 1) * 20

    while True:
        show_ship_status(ship)
        print("\n  ── Store Inventory ──")
        print(f"    [1] Repair hull    ({repair_cost} scrap per HP, need {ship['max_hull'] - ship['hull']} HP)")
        print(f"    [2] Buy fuel x5    ({fuel_cost * 5} scrap)")
        print(f"    [3] Buy missiles x3 ({missile_cost * 3} scrap)")
        print(f"    [4] Upgrade shields to Lv{ship['shields']+1} ({shield_cost} scrap)")
        print(f"    [5] Upgrade engines to Lv{ship.get('engines',1)+1} ({engine_cost} scrap)")
        for i, wname in enumerate(available_weapons):
            w = WEAPONS[wname]
            print(f"    [{6+i}] Buy {wname} (dmg:{w['damage']} pierce:{w['shield_pierce']}) — {w['cost']} scrap")
        print(f"    [0] Leave store")

        choice = input("\n  > ").strip()

        if choice == "0":
            break
        elif choice == "1":
            missing = ship["max_hull"] - ship["hull"]
            if missing == 0:
                print(yellow("  Hull is already full!"))
            else:
                affordable = min(missing, ship["scrap"] // repair_cost)
                if affordable == 0:
                    print(red("  Not enough scrap!"))
                else:
                    cost = affordable * repair_cost
                    ship["hull"] += affordable
                    ship["scrap"] -= cost
                    print(green(f"  Repaired {affordable} hull for {cost} scrap."))
        elif choice == "2":
            cost = fuel_cost * 5
            if ship["scrap"] >= cost:
                ship["scrap"] -= cost
                ship["fuel"] += 5
                print(green("  Bought 5 fuel."))
            else:
                print(red("  Not enough scrap!"))
        elif choice == "3":
            cost = missile_cost * 3
            if ship["scrap"] >= cost:
                ship["scrap"] -= cost
                ship["missiles"] += 3
                print(green("  Bought 3 missiles."))
            else:
                print(red("  Not enough scrap!"))
        elif choice == "4":
            if ship["scrap"] >= shield_cost:
                ship["scrap"] -= shield_cost
                ship["shields"] += 1
                shield_cost = 50 + ship["shields"] * 30
                print(green(f"  Shields upgraded to Level {ship['shields']}!"))
            else:
                print(red("  Not enough scrap!"))
        elif choice == "5":
            if ship["scrap"] >= engine_cost:
                ship["scrap"] -= engine_cost
                ship["engines"] = ship.get("engines", 1) + 1
                engine_cost = 30 + ship["engines"] * 20
                print(green(f"  Engines upgraded to Level {ship['engines']}!"))
            else:
                print(red("  Not enough scrap!"))
        elif choice.isdigit() and 6 <= int(choice) < 6 + len(available_weapons):
            idx = int(choice) - 6
            wname = available_weapons[idx]
            w = WEAPONS[wname]
            if ship["scrap"] >= w["cost"]:
                ship["scrap"] -= w["cost"]
                ship["weapons"].append(wname)
                available_weapons.pop(idx)
                print(green(f"  Bought {wname}!"))
            else:
                print(red("  Not enough scrap!"))
        else:
            print("  Invalid choice.")

# ─── SECTOR MAP ───────────────────────────────────────────────────────────────

def generate_sector(sector_num):
    """Return a list of beacons for this sector."""
    beacons = []
    for i in range(BEACONS_PER_SECTOR):
        r = random.random()
        if i == BEACONS_PER_SECTOR - 1:
            btype = "exit"
        elif r < 0.35:
            btype = "enemy"
        elif r < 0.55:
            btype = "event"
        elif r < 0.70:
            btype = "store"
        elif r < 0.85:
            btype = "empty"
        else:
            btype = "enemy"
        beacons.append({"type": btype, "visited": False, "index": i})
    return beacons

def show_sector_map(beacons, current, sector_num):
    icons = {"enemy": red("⚔"), "event": yellow("?"), "store": cyan("$"), "empty": "·", "exit": green("►")}
    visited_icon = "✓"
    print(f"\n  ── Sector {sector_num + 1}/{SECTOR_COUNT} Map ──\n")
    line = "  "
    for i, b in enumerate(beacons):
        if i == current:
            line += bold("[☆]")
        elif b["visited"]:
            line += f"[{visited_icon}]"
        else:
            line += f"[{icons.get(b['type'], '?')}]"
        if i < len(beacons) - 1:
            line += "──"
    print(line)
    print()

# ─── MAIN GAME LOOP ──────────────────────────────────────────────────────────

def title_screen():
    clear()
    print(cyan(r"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║       ███████╗████████╗██╗          ██╗   ██╗████████╗║
    ║       ██╔════╝╚══██╔══╝██║          ██║   ██║╚══██╔══╝║
    ║       █████╗     ██║   ██║          ██║   ██║   ██║   ║
    ║       ██╔══╝     ██║   ██║          ██║   ██║   ██║   ║
    ║       ██║        ██║   ███████╗     ╚██████╔╝   ██║   ║
    ║       ╚═╝        ╚═╝   ╚══════╝      ╚═════╝    ╚═╝   ║
    ║                   L  I  T  E                          ║
    ║                                                       ║
    ║         A Simplified Faster-Than-Light Roguelike       ║
    ╚═══════════════════════════════════════════════════════╝
    """))
    print("  Navigate 5 sectors. Fight enemies. Upgrade your ship.")
    print("  Defeat the Rebel Flagship to win!")
    print()
    input("  Press Enter to launch... ")

def game_over(ship, won=False):
    clear()
    if won:
        banner("★  VICTORY  ★", "═", 50)
        print(green("""
  The Rebel Flagship crumbles apart in a brilliant explosion.
  Your crew cheers as the Federation fleet rallies.
  The critical data has been delivered — the Rebellion is finished.

  Against all odds, the Federation survives.
  Congratulations, Commander!
        """))
    else:
        banner("GAME OVER", "═", 50)
        print(red("""
  Your ship breaks apart, debris scattering into the void.
  The Rebellion's advance continues unchecked.
  The Federation falls.
        """))
    print(f"  Final ship: {ship['name']}")
    print(f"  Surviving crew: {len(ship['crew'])}")
    print(f"  Scrap collected: {ship['scrap']}")
    pause("Press Enter to exit...")

def main():
    title_screen()

    ship = create_player_ship()

    for sector_num in range(SECTOR_COUNT):
        beacons = generate_sector(sector_num)
        current_beacon = 0
        beacons[0]["visited"] = True

        while True:
            clear()
            banner(f"SECTOR {sector_num + 1} / {SECTOR_COUNT}", "═")

            # Rebel fleet warning
            rebel_progress = sum(1 for b in beacons if b["visited"]) 
            if rebel_progress >= BEACONS_PER_SECTOR - 1:
                print(red("  ⚠  The rebel fleet is closing in! Proceed to the exit!"))

            show_sector_map(beacons, current_beacon, sector_num)
            show_ship_status(ship)

            # Check lose conditions
            if ship["hull"] <= 0:
                game_over(ship, won=False)
                return
            if not ship["crew"]:
                print(red("\n  All crew members have perished. The ship drifts lifelessly..."))
                game_over(ship, won=False)
                return
            if ship["fuel"] <= 0:
                print(red("\n  Out of fuel! The rebels catch up and destroy you."))
                game_over(ship, won=False)
                return

            # Choose next beacon
            reachable = []
            for i in range(max(0, current_beacon), min(len(beacons), current_beacon + 3)):
                if i != current_beacon:
                    reachable.append(i)
            # Always allow going forward at least 1
            if current_beacon + 1 < len(beacons) and (current_beacon + 1) not in reachable:
                reachable.append(current_beacon + 1)
            reachable = sorted(set(reachable))

            print("  Jump to beacon:")
            for idx in reachable:
                b = beacons[idx]
                visited = " (visited)" if b["visited"] else ""
                label = "EXIT" if b["type"] == "exit" else f"Beacon {idx + 1}"
                print(f"    [{idx + 1}] {label}{visited}")

            choice = input("\n  > ").strip()
            if not choice.isdigit():
                continue
            chosen = int(choice) - 1
            if chosen not in reachable:
                print("  Can't jump there.")
                pause()
                continue

            # Jump
            ship["fuel"] -= 1
            current_beacon = chosen
            beacon = beacons[chosen]
            beacon["visited"] = True

            clear()

            # Process beacon
            if beacon["type"] == "exit":
                print(green(f"\n  Jumping to Sector {sector_num + 2}..."))
                pause()
                break

            elif beacon["type"] == "enemy":
                enemy = make_enemy(sector_num)
                result = combat(ship, enemy)
                if result is False:
                    game_over(ship, won=False)
                    return
                # fled → just continue

            elif beacon["type"] == "event":
                event = get_event(sector_num, ship)
                banner("EVENT", "─")
                print(f"\n  {event['text']}\n")
                for i, c in enumerate(event["choices"]):
                    print(f"    [{i+1}] {c['label']}")
                ch = input("\n  > ").strip()
                if ch.isdigit() and 1 <= int(ch) <= len(event["choices"]):
                    result_text = event["choices"][int(ch)-1]["fn"]()
                else:
                    result_text = event["choices"][0]["fn"]()
                print(f"\n  {result_text}")
                pause()

            elif beacon["type"] == "store":
                visit_store(ship)

            elif beacon["type"] == "empty":
                msgs = [
                    "Nothing here but the hum of your engines.",
                    "Empty space. At least it's peaceful.",
                    "A quiet beacon. Your crew takes a breather.",
                    "Sensor sweep reveals nothing of interest.",
                ]
                print(f"\n  {random.choice(msgs)}")
                pause()

            # Check hull after events
            if ship["hull"] <= 0:
                game_over(ship, won=False)
                return

    # ── FINAL BATTLE ──
    clear()
    banner("THE LAST STAND", "█")
    print("""
  You've reached Federation headquarters — but the Rebel Flagship
  has arrived first. It's now or never, Commander.
  
  Defeat the Flagship in a three-phase battle to save the Federation!
    """)
    pause("Press Enter to begin the final battle...")

    if flagship_combat(ship):
        game_over(ship, won=True)
    else:
        game_over(ship, won=False)


if __name__ == "__main__":
    main()
