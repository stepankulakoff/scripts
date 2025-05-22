import os
import re

def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def chunk_sentences(sentences, max_length):
    chunks, current = [], ''
    for s in sentences:
        if len(current) + len(s) + 1 <= max_length:
            current += s + ' '
        else:
            chunks.append(current.strip())
            current = s + ' '
    if current:
        chunks.append(current.strip())
    return chunks

def process_file(input_path, max_length):
    # Директория, где лежит сам скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Её родитель — на уровень выше
    parent_dir = os.path.dirname(script_dir)
    # Папка output_10000 именно там
    output_dir = os.path.join(parent_dir, 'output_5000')
    os.makedirs(output_dir, exist_ok=True)

    content = open(input_path, 'r', encoding='utf-8').read()
    parts   = content.split('•')
    file_id = 1

    for part in parts[1:]:
        chapter   = '•' + part.strip()
        sentences = split_sentences(chapter)
        chunks    = chunk_sentences(sentences, max_length)
        for chunk in chunks:
            fname = os.path.join(output_dir, f'chunk_{file_id:03d}.txt')
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(chunk)
            print(f"Wrote {fname}")
            file_id += 1

# Пример вызова
process_file(
    '/Users/stepankulakov/Desktop/ontology_driven_llm_knowldedge_version/text.txt',
    max_length=5000
)
