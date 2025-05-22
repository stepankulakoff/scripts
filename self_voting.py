#!/usr/bin/env python3


import os, time, collections, pathlib, random
from openai import OpenAI

# ────────────────────────── ПАРАМЕТРЫ ────────────────────────── #
N_RUNS = 5              # 
VOTE_K = (N_RUNS // 2) + 1 # 
TEMP   = 0.5              # t
MODEL  = "gpt-4o"     #

client = OpenAI(api_key="") 

BASE_DIR     = pathlib.Path(__file__).resolve().parents[1]
INPUT_DIR    = BASE_DIR / "output_5000"
OUTPUT_FILE  = BASE_DIR / "results" / "all_ru.txt"
PROMPT_FILE  = BASE_DIR / "prompts" / "simple.txt"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ───────────────────── загрузка шаблона ─────────────────────── #
def load_prompt_template() -> str:
    with open(PROMPT_FILE, encoding="utf-8") as f:
        return f.read()

PROMPT_TEMPLATE = load_prompt_template()

# ────────────────────── GPT‑вызов одиночный ─────────────────── #
def gpt_triples(text: str, seed: int) -> list[str]:
    prompt = PROMPT_TEMPLATE.replace("<<<TEXT>>>", text.strip())
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=TEMP,
        seed=seed,
        messages=[
            {"role": "system",
             "content": "Ты помощник по извлечению графа знаний, использующий предопределенную онтологию."},
            {"role": "user", "content": prompt}
        ]
    )
    raw = resp.choices[0].message.content
    #print(raw)
    # оставляем строки, начинающиеся на '('
    triples = [ln.strip() for ln in raw.splitlines() if ln.strip().startswith("(")]
    return triples
# ─────────────── Self‑consistency + подсчёт голосов ──1──────── #
def extract_consistent(text: str) -> str:
    votes = collections.Counter()
    for run in range(N_RUNS):
        triples = gpt_triples(text, seed=run)
        votes.update(triples)
        time.sleep(0.4)           # немного бережём rate‑limit

    final = [t for t, c in votes.items() if c >= VOTE_K]
    return "\n".join(sorted(final))

# ───────────────────────────── main ─────────────────────────── #
def main():
    txt_files = sorted(p for p in os.listdir(INPUT_DIR) if p.endswith(".txt"))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for fname in txt_files:
            path = INPUT_DIR / fname
            print(f"📄 Processing {fname} …")
            text = path.read_text(encoding="utf-8")
            triples = extract_consistent(text)
            out.write(triples + "\n\n")

    print(f"✅ Все тройки сохранены в: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
