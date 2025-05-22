#!/usr/bin/env python3

import os, sys, json, textwrap, urllib.parse, urllib.request, pathlib
from openai import OpenAI

# ── НАСТРОЙ ───────────────────────────────────────────────────────────────
BASE_DIR     = pathlib.Path(__file__).resolve().parents[1]
INPUT_DIR    = BASE_DIR / "output_5000"
OUTPUT_FILE  = BASE_DIR / "results" / "wiki_annotate.txt"

USER_KEY      = ""
OPENAI_KEY    = ""
MODEL         = "gpt-4o"
LANG          = "ru"
TOP_K         = 20
# ───────────────────────────────────────────────────────────────────────────

WIKIFIER_URL = "http://www.wikifier.org/annotate-article"
client       = OpenAI(api_key=OPENAI_KEY)

# ── WIKIFIER ───────────────────────────────────────────────────────────────
def call_wikifier(text: str) -> dict:
    params = urllib.parse.urlencode([
        ("text", text), ("lang", LANG), ("userKey", USER_KEY),
        ("includeCosines", "true"), ("support", "true"),
        ("dbPediaTypes", "true"),
        ("wikiDataClasses", "false"), ("wikiDataClassIds", "false"),
        ("applyPageRankSqThreshold", "true"), ("pageRankSqThreshold", "0.8"),
    ]).encode()
    req = urllib.request.Request(
        WIKIFIER_URL, data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)

def top_entities(w_json: dict, k: int):
    scored = []
    for ann in w_json.get("annotations", []):
        types = ann.get("dbPediaTypes") or []
        if not types:
            continue
        score = ann.get("cosine", 0) * ann.get("supportLen", len(ann.get("support", [])))
        scored.append((score, ann["title"], types))
    scored.sort(reverse=True)
    return [(t, typs) for _, t, typs in scored[:k]]

# ── GPT-disambiguation ────────────────────────────────────────────────────
def pick_types_llm(entities, context):
    ent_block = "\n".join(
        f"- {title}: {', '.join('dbo:' + t for t in types)}"
        for title, types in entities)
    sys_msg = ("Ты — эксперт по онтологии DBpedia. "
               "Для каждой сущности выбери ровно ОДИН класс dbo:*.")
    usr_msg = textwrap.dedent(f"""
        Текст:
        \"\"\"{context}\"\"\"

        Сущности + кандидаты:
        {ent_block}

        Ответь ЧИСТЫМ JSON-объектом {{ "Сущность": "dbo:Класс", ... }}
    """)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": sys_msg},
                  {"role": "user",   "content": usr_msg}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(resp.choices[0].message.content)

# ── MAIN (batch) ──────────────────────────────────────────────────────────
# ── MAIN (batch) ──────────────────────────────────────────────────────────
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    txt_files = sorted(p for p in os.listdir(INPUT_DIR) if p.endswith(".txt"))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for fname in txt_files:
            path = INPUT_DIR / fname
            print(f"📄 Processing {fname} …")
            text = path.read_text(encoding="utf-8")

            # 1) Wikifier
            w_json   = call_wikifier(text)
            entities = top_entities(w_json, TOP_K)
            print(entities)
            if not entities:
                print("   ⚠️  No valid entities.")
                continue

            # 2) LLM-дисамбигуация
            chosen = pick_types_llm(entities, text)

            # 3) ── Запись в файл ───────────────────────────────────────────
            out.write(f"# {fname}\n")

            # 3-a) кандидаты ДО дисамбигуации
            out.write("# candidates (raw Wikifier)\n")
            for title, types in entities:
                joined = ", ".join("dbo:" + t for t in types)
                print(joined)
                out.write(f"{title}: {joined}\n")

            # 3-b) итоговые тройки
            out.write("# triples (LLM choice)\n")
            for title, _ in entities:
                cls = chosen.get(title, "Unknown")
                out.write(f"({title}, type, {cls})\n")
            out.write("\n")

    print(f"\n✅ Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
