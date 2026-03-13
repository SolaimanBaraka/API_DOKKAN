"""
scraper/fandom_scraper.py   v2

Scraper real de la Fandom Wiki de Dokkan Battle.

Estrategia verificada contra la wiki real:
1. Leer pginas "All Cards: (1)001 to (1)100"  lista de ttulos + IDs
2. Para cada carta, leer wikitext y parsear template {{Characters
3. Insertar/actualizar en BD
"""

import re
import json
import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

WIKI_API      = "https://dbz-dokkanbattle.fandom.com/api.php"
WIKI_BASE     = "https://dbz-dokkanbattle.fandom.com"
REQUEST_DELAY = 0.8

HEADERS = {
    "User-Agent": "DokkanAPI-Bot/2.0 (fan project, non-commercial)"
}

ALL_CARD_INDEX_PAGES = [
    "All Cards: (1)001 to (1)100",   "All Cards: (1)101 to (1)200",
    "All Cards: (1)201 to (1)300",   "All Cards: (1)301 to (1)400",
    "All Cards: (1)401 to (1)500",   "All Cards: (1)501 to (1)600",
    "All Cards: (1)601 to (1)700",   "All Cards: (1)701 to (1)800",
    "All Cards: (1)801 to (1)900",   "All Cards: (1)901 to (1)1000",
    "All Cards: (1)1001 to (1)1100", "All Cards: (1)1101 to (1)1200",
    "All Cards: (1)1201 to (1)1300", "All Cards: (1)1301 to (1)1400",
    "All Cards: (1)1401 to (1)1500", "All Cards: (1)1501 to (1)1600",
    "All Cards: (1)1601 to (1)1700", "All Cards: (1)1701 to (1)1800",
    "All Cards: (1)1801 to (1)1900", "All Cards: (1)1901 to (1)2000",
    "All Cards: (1)2001 to (1)2100", "All Cards: (1)2101 to (1)2200",
    "All Cards: (1)2201 to (1)2300", "All Cards: (1)2301 to (1)2400",
    "All Cards: (1)2401 to (1)2500", "All Cards: (1)2501 to (1)2600",
    "All Cards: (1)2601 to (1)2700", "All Cards: (1)2701 to (1)2800",
    "All Cards: (1)2801 to (1)2900",
    "All Cards: (2)001 to (2)1000",
    "All Cards: (3)001 to (3)1000",
    "All Cards: (4)001 to (4) unknown",
]


def _api_get(params: dict) -> dict:
    for attempt in range(3):
        try:
            r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning(f"[Intento {attempt+1}/3] {e}")
            time.sleep(2 ** attempt)
    return {}


def _get_wikitext(page_title: str) -> str:
    data = _api_get({
        "action": "parse", "page": page_title,
        "prop": "wikitext", "format": "json",
    })
    return data.get("parse", {}).get("wikitext", {}).get("*", "")


def _field(wikitext: str, field: str) -> Optional[str]:
    """Extrae valor de campo de template MediaWiki."""
    escaped = re.escape(field)
    m = re.search(rf"\|\s*{escaped}\s*=\s*(.*?)(?=\n\s*\||\n\s*\}}|\Z)", wikitext, re.DOTALL)
    return m.group(1).strip() if m else None


def _clean(text: str) -> str:
    """Limpia wikitext: links, refs, tags HTML."""
    if not text:
        return ""
    # [[File:AGL icon.png|30px|link=Category:AGL]]  AGL
    text = re.sub(r"\[\[File:[^|]+icon\.png[^\]]*\|link=Category:([A-Z]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[[^\]]*\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    # Convertir iconos de tipo [[File:AGL icon.png|...|link=Category:AGL]]  AGL
    text = re.sub(r"\[\[File:[^|]+icon\.png[^]]*\|link=Category:([A-Z]+)\]\]", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    text = re.sub(r"'{2,3}", "", text)
    return " ".join(text.split()).strip()


def _to_int(val) -> Optional[int]:
    if val is None:
        return None
    digits = re.sub(r"[^\d]", "", str(val).split("/")[0])
    return int(digits) if digits else None


def _parse_list(text: str) -> list:
    if not text:
        return []
    cleaned = _clean(text)
    parts = re.split(r"\s+-\s+(?=[A-Z('])", cleaned)
    result = []
    for p in parts:
        for sub in p.split(","):
            s = sub.strip()
            if s and len(s) > 1:
                result.append(s)
    return result


def parse_index_page(index_title: str) -> list[dict]:
    """Lee una pgina ndice y devuelve lista de {wiki_page, card_id, rarity, type}."""
    wikitext = _get_wikitext(index_title)
    if not wikitext:
        return []

    entries = []
    # Patrn de fila en la tabla de All Cards
    # |(1)001\n|1000010\n|[[File:...]]\n|[[Pgina wiki|Texto mostrado]]\n|[[File:SSR eclair...]]\n|[[File:AGL icon...]]
    row_re = re.compile(
        r"\|\(\w\)(\d+)\s*\n"          # nmero de carta
        r"\|(\d+)\s*\n"                 # card_id
        r"\|\s*\[\[File:[^\n]+\n"       # icono thumb
        r"\|\s*\[\[([^\|\]\n]+)",       # ttulo de la pgina wiki
        re.MULTILINE
    )

    for m in row_re.finditer(wikitext):
        card_num, card_id, wiki_page = m.group(1), m.group(2), m.group(3).strip()

        # Buscar rareza y tipo en las siguientes lneas despus de este match
        context = wikitext[m.start():m.start()+500]
        rarity_m = re.search(r"\[\[File:(LR|UR|SSR|SR|R|N)\s+eclair", context)
        type_m   = re.search(r"\[\[File:(AGL|TEQ|INT|STR|PHY)\s+icon", context)

        entries.append({
            "wiki_page": wiki_page,
            "card_id":   card_id,
            "rarity":    rarity_m.group(1) if rarity_m else "",
            "type":      type_m.group(1)   if type_m   else "",
        })

    logger.info(f"'{index_title}': {len(entries)} cartas en ndice")
    return entries


def parse_card_page(wiki_title: str, fallback: dict = None) -> Optional[dict]:
    """Parsea la pgina individual de una carta."""
    wikitext = _get_wikitext(wiki_title)
    if not wikitext or "{{Characters" not in wikitext:
        return None

    f = lambda field: _field(wikitext, field)

    name1    = _clean(f("name1") or "")
    name2    = _clean(f("name2") or "")
    full_name = f"{name1} {name2}".strip() if name1 else name2

    rarity   = (f("rarity") or (fallback or {}).get("rarity", "")).upper().strip()
    raw_type = (f("type")   or (fallback or {}).get("type", "")).upper().strip()
    card_type = raw_type[:3] if len(raw_type) >= 3 else raw_type

    # ID de imagen para construir URL thumb
    thumb_m = re.search(r"Card[_ ](\d+)[_ ]thumb\.png", wikitext)
    image_url = None
    thumb_url = None
    if thumb_m:
        fid = thumb_m.group(1)
        image_url = (
            f"https://static.wikia.nocookie.net/dbz-dokkanbattle/images/"
            f"thumb/Card_{fid}_thumb.png/120px-Card_{fid}_thumb.png"
        )
        thumb_url = (
            f"https://static.wikia.nocookie.net/dbz-dokkanbattle/images/"
            f"thumb/Card_{fid}_thumb.png/60px-Card_{fid}_thumb.png"
        )

    cost_raw = f("cost") or ""
    cost_parts = [int(x) for x in re.findall(r"\d+", cost_raw)]
    cost = max(cost_parts) if cost_parts else None

    # Habilidades
    ls_desc  = _clean(f("LS description") or "")
    sa_name  = _clean(f("SA name")  or "")
    sa_desc  = _clean(f("SA description") or "")
    sa2_name = _clean(f("SA2 name") or "")
    sa2_desc = _clean(f("SA2 description") or "")
    ps_name  = _clean(f("PS name")  or "")
    ps_desc  = _clean(f("PS description") or "")
    as_name  = _clean(f("AS name")  or "")
    as_desc  = _clean(f("AS description") or "")
    as_cond  = _clean(f("AS condition") or "")

    super_attack  = f"{sa_name}  {sa_desc}".strip(" ") if (sa_name or sa_desc) else None
    ultra_sa      = f"{sa2_name}  {sa2_desc}".strip(" ") if (sa2_name or sa2_desc) else None
    passive       = f"{ps_name}: {ps_desc}".strip(": ")   if (ps_name or ps_desc) else None
    active        = f"{as_name}: {as_desc}".strip(": ")   if (as_name or as_desc) else None

    # Habilidades EZA
    eza_ls_desc = _clean(f("EZA LS description") or "")
    eza_ps_name = _clean(f("EZA PS name") or "")
    eza_ps_desc = _clean(f("EZA PS description") or "")
    eza_sa_name = _clean(f("EZA SA name") or "")
    eza_sa_desc = _clean(f("EZA SA description") or "")

    eza_passive = f"{eza_ps_name}: {eza_ps_desc}".strip(": ") if (eza_ps_name or eza_ps_desc) else None
    eza_sa      = f"{eza_sa_name}: {eza_sa_desc}".strip(": ") if (eza_sa_name or eza_sa_desc) else None

    # Medallas de despertar (Dokkan Awakening)
    medals = []
    for i in range(1, 9):
        medal_name = _clean(f(f"Awaken medal {i}") or "")
        medal_qty  = _to_int(f(f"Awaken medal {i} qty"))
        if medal_name:
            medals.append({"name": medal_name, "quantity": medal_qty or 0})

    # Condición de transformación
    transform_cond = _clean(f("Transform condition") or f("Transformation condition") or "")

    categories  = _parse_list(f("Category") or "")
    link_skills = _parse_list(f("Link skill") or "")

    is_lr   = rarity == "LR"
    summon  = (f("Summon") or "").upper()
    is_df   = "DF" in summon
    is_eza  = bool(f("EZA PS description") or f("EZA LS description"))
    is_transformable = bool(f("Transform condition") or f("Transformation condition") or f("Transform type"))

    jp_date  = (f("JPdate")  or "").strip()
    glb_date = (f("GLBdate") or "").strip()

    return {
        "wiki_id":       wiki_title.replace(" ", "_"),
        "name":          name2 or name1 or wiki_title,
        "title":         name1 or None,
        "full_name":     full_name or wiki_title,
        "rarity":        rarity or None,
        "type":          card_type or None,
        "cost":          cost,
        "hp_max":        _to_int(f("HP max")),
        "atk_max":       _to_int(f("ATK max")),
        "def_max":       _to_int(f("DEF max")),
        "hp_eza":        _to_int(f("EZA HP max")),
        "atk_eza":       _to_int(f("EZA ATK max")),
        "def_eza":       _to_int(f("EZA DEF max")),
        "leader_skill":  ls_desc or None,
        "super_attack":  super_attack,
        "ultra_super_attack": ultra_sa,
        "passive_skill": passive,
        "active_skill":  active,
        "active_skill_condition": as_cond or None,
        "eza_leader_skill":  eza_ls_desc or None,
        "eza_passive_skill": eza_passive,
        "eza_super_attack":  eza_sa,
        "categories":    json.dumps(categories),
        "link_skills":   json.dumps(link_skills),
        "awakening_medals": json.dumps(medals) if medals else None,
        "is_transformable": is_transformable,
        "transformation_conditions": transform_cond or None,
        "is_lr":         is_lr,
        "is_eza":        is_eza,
        "is_dokkan_fest": is_df,
        "image_url":     image_url,
        "thumb_url":     thumb_url,
        "wiki_url":      f"{WIKI_BASE}/wiki/{wiki_title.replace(' ', '_')}",
        "jp_release_date":  jp_date or None,
        "glb_release_date": glb_date or None,
    }


def scrape_cards(
    index_pages:      list  = None,
    max_cards:        int   = 100,
    rarity_filter:    list  = None,
    progress_callback       = None,
) -> list[dict]:
    """
    Scrapea cartas de la wiki.

    Args:
        index_pages:   Pginas ndice a procesar. None = todas.
        max_cards:     Mximo de cartas a importar.
        rarity_filter: Solo estas rarezas, ej: ["LR", "UR"]
        progress_callback: fn(actual, total, nombre) para log de progreso.
    """
    pages = index_pages or ALL_CARD_INDEX_PAGES

    logger.info(f"=== FASE 1: Leyendo ndices ({len(pages)} pginas) ===")
    all_entries = []
    for idx_page in pages:
        entries = parse_index_page(idx_page)
        if rarity_filter:
            rf = [r.upper() for r in rarity_filter]
            entries = [e for e in entries if e["rarity"].upper() in rf]
        all_entries.extend(entries)
        time.sleep(REQUEST_DELAY)
        if len(all_entries) >= max_cards:
            break

    # Deduplicar
    seen, unique = set(), []
    for e in all_entries:
        if e["wiki_page"] not in seen:
            seen.add(e["wiki_page"])
            unique.append(e)
    unique = unique[:max_cards]

    logger.info(f"=== FASE 2: Parseando {len(unique)} pginas de cartas ===")
    cards = []
    for i, entry in enumerate(unique):
        title = entry["wiki_page"]
        logger.info(f"[{i+1}/{len(unique)}] {title}")
        card = parse_card_page(title, fallback=entry)
        if card:
            if not card.get("rarity") and entry.get("rarity"):
                card["rarity"] = entry["rarity"]
            if not card.get("type") and entry.get("type"):
                card["type"] = entry["type"]
            cards.append(card)
        if progress_callback:
            progress_callback(i + 1, len(unique), title)
        time.sleep(REQUEST_DELAY)

    logger.info(f"=== Completado: {len(cards)} cartas importadas ===")
    return cards


def scrape_character(character_name: str, max_cards: int = 50) -> list[dict]:
    """Scrapea todas las cartas de un personaje. Ej: scrape_character('Goku')"""
    data = _api_get({
        "action": "query", "list": "categorymembers",
        "cmtitle": f"Category:{character_name}_Cards",
        "cmlimit": max_cards, "format": "json",
    })
    members = data.get("query", {}).get("categorymembers", [])
    cards = []
    for m in members:
        card = parse_card_page(m["title"])
        if card:
            cards.append(card)
        time.sleep(REQUEST_DELAY)
    return cards


def scrape_latest_cards(pages_back: int = 2) -> list[dict]:
    """Scrapea las pginas ms recientes del ndice."""
    return scrape_cards(
        index_pages=ALL_CARD_INDEX_PAGES[-pages_back:],
        max_cards=pages_back * 100
    )
