"""
scraper/seed.py

Inserta datos de ejemplo reales para poder probar la API
inmediatamente sin necesidad de hacer scraping completo.

Ejecutar: python -m scraper.seed
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.card import Card
from app.models.event import Event
from app.models.banner import Banner
from app.models.item import Item

#  DATOS DE EJEMPLO 

SAMPLE_CARDS = [
    {
        "wiki_id": "Super_Saiyan_Goku",
        "name": "Goku",
        "title": "Super Saiyan",
        "full_name": "Super Saiyan Goku",
        "rarity": "SSR",
        "type": "AGL",
        "cost": 32,
        "hp_max": 9274,
        "atk_max": 8537,
        "def_max": 4901,
        "leader_skill": "AGL Type Ki +3 and HP, ATK & DEF +70%",
        "super_attack": "Kamehameha  Raises ATK & DEF and causes immense damage to enemy",
        "passive_skill": "Golden Warrior  Ki +4 and ATK & DEF +100% when HP is 50% or above",
        "categories": json.dumps(["Super Saiyan", "Full Power", "Kamehameha", "Goku's Family"]),
        "link_skills": json.dumps(["Super Saiyan", "Kamehameha", "Golden Warrior", "Prepared for Battle"]),
        "is_lr": False, "is_eza": True, "is_dokkan_fest": False,
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Super_Saiyan_Goku",
        "image_url": "https://vignette.wikia.nocookie.net/dbz-dokkanbattle/images/thumb/Super_Saiyan_Goku_SSR_AGL_card.png",
    },
    {
        "wiki_id": "Ultra_Instinct_Goku",
        "name": "Goku (Ultra Instinct)",
        "title": "Transcendent Instinct",
        "full_name": "Transcendent Instinct Goku (Ultra Instinct)",
        "rarity": "LR",
        "type": "AGL",
        "cost": 59,
        "hp_max": 22428,
        "atk_max": 24000,
        "def_max": 14000,
        "hp_eza": 26428,
        "atk_eza": 28000,
        "def_eza": 17000,
        "leader_skill": "All Types Ki +4, HP, ATK & DEF +170%",
        "super_attack": "Godly Display  Raises ATK & DEF, then causes mega-colossal damage",
        "ultra_super_attack": "Surpassing All  Raises ATK, lowers DEF and causes mega-colossal damage to all enemies",
        "passive_skill": "Power Without Limits  Ki +5, ATK +200% and DEF +150% at start of turn; attacks become critical when performing 8+ attacks in a turn",
        "active_skill": "Mastered Ultra Instinct  Deals 7 critical hits, then all enemies' DEF -100% for 3 turns",
        "active_skill_condition": "Can be activated when 20 or more Ki Spheres are obtained in battle",
        "categories": json.dumps(["God Ki", "Pure Saiyans", "Kamehameha", "Goku's Family", "Ultra Instinct"]),
        "link_skills": json.dumps(["Super Saiyan", "Kamehameha", "Golden Warrior", "Prepared for Battle", "Over in a Flash", "Universe's Most Powerful"]),
        "is_lr": True, "is_eza": True, "is_dokkan_fest": True,
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Transcendent_Instinct_-Sign-_Goku_(Ultra_Instinct)",
        "image_url": "https://vignette.wikia.nocookie.net/dbz-dokkanbattle/images/UI_Goku_LR_AGL.png",
    },
    {
        "wiki_id": "Vegeta_SSJ_Blue",
        "name": "Vegeta (Super Saiyan God SS)",
        "title": "Unparalleled Saiyan Pride",
        "full_name": "Unparalleled Saiyan Pride Vegeta (Super Saiyan God SS)",
        "rarity": "UR",
        "type": "TEQ",
        "cost": 48,
        "hp_max": 14375,
        "atk_max": 15438,
        "def_max": 8250,
        "leader_skill": "TEQ Type Ki +3, HP & ATK & DEF +120%",
        "super_attack": "Final Flash  Causes immense damage to enemy and lowers ATK & DEF",
        "passive_skill": "Saiyan Elite  ATK & DEF +120%; additional Ki +3 when facing Super-type enemies",
        "categories": json.dumps(["God Ki", "Super Saiyan", "Vegeta's Family", "Rival Duo", "Bond of Father and Son"]),
        "link_skills": json.dumps(["Super Saiyan", "Golden Warrior", "Prepared for Battle", "Royal Lineage", "Saiyan Warrior Race"]),
        "is_lr": False, "is_eza": False, "is_dokkan_fest": False,
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Vegeta_SSJ_Blue",
        "image_url": "https://vignette.wikia.nocookie.net/dbz-dokkanbattle/images/Vegeta_SSGSS_TEQ.png",
    },
    {
        "wiki_id": "Frieza_Golden",
        "name": "Frieza (Golden)",
        "title": "Terror Returned to Life",
        "full_name": "Terror Returned to Life Frieza (Golden)",
        "rarity": "LR",
        "type": "PHY",
        "cost": 59,
        "hp_max": 19850,
        "atk_max": 21200,
        "def_max": 11800,
        "leader_skill": "PHY Type Ki +4 and HP, ATK & DEF +150%",
        "super_attack": "Death Beam  Causes mega-colossal damage to enemy and lowers DEF",
        "passive_skill": "Overwhelming Power  Ki +5, ATK +200%; counters with tremendous power when attacked",
        "categories": json.dumps(["Wicked Bloodline", "Universe's Most Powerful", "Frieza Saga", "Resurrection 'F'"]),
        "link_skills": json.dumps(["Universe's Most Powerful", "Brutal Beatdown", "Shocking Speed", "Fierce Battle"]),
        "is_lr": True, "is_eza": False, "is_dokkan_fest": True,
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Golden_Frieza",
        "image_url": "https://vignette.wikia.nocookie.net/dbz-dokkanbattle/images/Golden_Frieza_LR_PHY.png",
    },
    {
        "wiki_id": "Gohan_Beast",
        "name": "Gohan (Beast)",
        "title": "Awakened Beast",
        "full_name": "Awakened Beast Gohan (Beast)",
        "rarity": "LR",
        "type": "TEQ",
        "cost": 59,
        "hp_max": 20500,
        "atk_max": 22800,
        "def_max": 13100,
        "leader_skill": "TEQ Type Ki +4, HP, ATK & DEF +170%; plus an additional ATK & DEF +30% for \"Goku's Family\" Category",
        "super_attack": "Perfected Evolution Kamehameha  Raises ATK, causes mega-colossal damage to all enemies and lowers ATK & DEF",
        "passive_skill": "Absolute Power  Ki +5, ATK & DEF +200%; launches an additional attack that has a medium chance of becoming a Super Attack",
        "categories": json.dumps(["Hybrid Saiyans", "Goku's Family", "Kamehameha", "Galactic Patrol", "Inhuman Deeds"]),
        "link_skills": json.dumps(["Kamehameha", "Super Saiyan", "Prepared for Battle", "Fierce Battle", "Shattering the Limit"]),
        "is_lr": True, "is_eza": False, "is_dokkan_fest": True,
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Gohan_Beast",
        "image_url": "https://vignette.wikia.nocookie.net/dbz-dokkanbattle/images/Gohan_Beast_LR_TEQ.png",
    },
]

SAMPLE_EVENTS = [
    {
        "wiki_id": "11th_anniversary_part2",
        "name": "11th Anniversary Super Maximum Celebration - Part 2",
        "type": "special",
        "description": "Celebrate the 11th Anniversary of Dokkan Battle with special stages, missions and exclusive rewards.",
        "is_active": True,
        "start_date": "2025-07-14",
        "end_date": "2025-08-10",
        "difficulties": json.dumps(["Normal", "Hard", "Z-Hard", "Super2"]),
        "stamina_cost": 15,
        "rewards": json.dumps(["Dragon Stone x30", "Awakening Medal Set", "LR Ticket"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/11th_Anniversary",
    },
    {
        "wiki_id": "Strike_Event_Gohan",
        "name": "Strike Event - Gohan (Beast)",
        "type": "strike",
        "description": "Fight against the Beast Gohan in this limited-time Strike Event.",
        "is_active": True,
        "start_date": "2025-07-20",
        "end_date": "2025-07-27",
        "difficulties": json.dumps(["Z-Hard", "Super2", "Super3"]),
        "stamina_cost": 10,
        "rewards": json.dumps(["Awakening Medal x5", "Dragon Stone x3"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Strike_Event_Gohan_Beast",
    },
    {
        "wiki_id": "World_Tournament_2025",
        "name": "World Tournament - July 2025",
        "type": "world_tournament",
        "description": "Battle against other players' teams in the World Tournament for rankings and prizes.",
        "is_active": False,
        "start_date": "2025-07-01",
        "end_date": "2025-07-08",
        "difficulties": json.dumps(["Preliminary", "Quarter-Final", "Semi-Final", "Final"]),
        "stamina_cost": 0,
        "rewards": json.dumps(["Dragon Stone x5", "World Tournament Coin x100"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/World_Tournament",
    },
]

SAMPLE_BANNERS = [
    {
        "wiki_id": "11th_anniversary_dokkan_fest_2025",
        "name": "11th Anniversary Dokkan Festival",
        "type": "dokkan_fest",
        "description": "The biggest banner of the year! Limited characters exclusive to the 11th Anniversary.",
        "is_active": True,
        "start_date": "2025-07-14",
        "end_date": "2025-08-10",
        "featured_cards": json.dumps(["Ultra Instinct Goku", "Gohan (Beast)", "Vegeta (Ultra Ego)"]),
        "pool_cards": json.dumps(["Ultra Instinct Goku", "Gohan (Beast)", "Frieza (Golden)", "Super Saiyan Goku"]),
        "single_cost": 5,
        "multi_cost": 50,
        "rates": json.dumps({"LR": "3%", "UR": "5%", "SSR": "22%", "SR": "70%"}),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/11th_Anniversary_Dokkan_Fest",
    },
    {
        "wiki_id": "legendary_summon_july_2025",
        "name": "Legendary Summon - July 2025",
        "type": "legendary_summon",
        "description": "Legendary Summon featuring classic fan-favourite characters.",
        "is_active": True,
        "start_date": "2025-07-15",
        "end_date": "2025-08-05",
        "featured_cards": json.dumps(["Super Saiyan Goku", "Vegeta (Super Saiyan God SS)"]),
        "pool_cards": json.dumps(["Super Saiyan Goku", "Vegeta (Super Saiyan God SS)", "Frieza (Golden)"]),
        "single_cost": 5,
        "multi_cost": 50,
        "rates": json.dumps({"SSR": "7.5%", "SR": "22.5%", "R": "70%"}),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Legendary_Summon",
    },
]

SAMPLE_ITEMS = [
    {
        "wiki_id": "dragon_stone",
        "name": "Dragon Stone",
        "category": "dragon_stone",
        "description": "The premium currency of Dokkan Battle. Used for summoning and reviving.",
        "effect": "Can be used to perform a single summon (5 stones) or revive in battle (1 stone).",
        "usable_in_battle": True,
        "max_stack": 9999,
        "how_to_obtain": json.dumps(["Login bonus", "Events", "Missions", "Story completion"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Dragon_Stone",
    },
    {
        "wiki_id": "senzu_bean",
        "name": "Senzu Bean",
        "category": "recovery",
        "description": "Fully restores one character's HP.",
        "effect": "Restores 100% HP to one character.",
        "usable_in_battle": True,
        "max_stack": 3,
        "how_to_obtain": json.dumps(["Events", "Missions"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Senzu_Bean",
    },
    {
        "wiki_id": "kaioken_training",
        "name": "Kaioken Training",
        "category": "training",
        "description": "Training item that increases ATK for one character.",
        "effect": "ATK +700",
        "usable_in_battle": False,
        "max_stack": 99,
        "how_to_obtain": json.dumps(["Training events", "Baba Shop"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/Kaioken_Training",
    },
    {
        "wiki_id": "agl_orb",
        "name": "AGL Orb",
        "category": "orb",
        "description": "Orb used to awaken AGL-type characters.",
        "effect": "Required for Dokkan Awakening of AGL-type characters.",
        "usable_in_battle": False,
        "max_stack": 9999,
        "how_to_obtain": json.dumps(["Orb collection stages", "Events"]),
        "wiki_url": "https://dbz-dokkanbattle.fandom.com/wiki/AGL_Orb",
    },
]


#  EJECUCIN 

def run_seed():
    init_db()
    db = SessionLocal()

    print(" Iniciando seed de datos...")

    # Limpiar tablas
    db.query(Card).delete()
    db.query(Event).delete()
    db.query(Banner).delete()
    db.query(Item).delete()
    db.commit()

    # Insertar cartas
    for data in SAMPLE_CARDS:
        db.add(Card(**data))
    db.commit()
    print(f"  [OK] {len(SAMPLE_CARDS)} cartas insertadas")

    # Insertar eventos
    for data in SAMPLE_EVENTS:
        db.add(Event(**data))
    db.commit()
    print(f"  [OK] {len(SAMPLE_EVENTS)} eventos insertados")

    # Insertar banners
    for data in SAMPLE_BANNERS:
        db.add(Banner(**data))
    db.commit()
    print(f"  [OK] {len(SAMPLE_BANNERS)} banners insertados")

    # Insertar items
    for data in SAMPLE_ITEMS:
        db.add(Item(**data))
    db.commit()
    print(f"  [OK] {len(SAMPLE_ITEMS)} items insertados")

    db.close()
    print("\n Seed completado. La API ya tiene datos para probar.")


if __name__ == "__main__":
    run_seed()
