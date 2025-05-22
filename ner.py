#!/usr/bin/env python3
import re
import sys

def extract_dbo_classes(file_path: str) -> set:
    """Извлекает уникальные классы типа dbo:* из файла."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return set(re.findall(r'dbo:\w+', content))


def main():
    if len(sys.argv) != 2:
        print("❗ Укажите путь к файлу с тройками.")
        print("🔧 Пример: python extract_unique_classes.py triples.txt")
        return

    file_path = sys.argv[1]
    classes = extract_dbo_classes(file_path)

    print(f"🔍 Найдено {len(classes)} уникальных классов:\n")
    for cls in sorted(classes):
        print(f"• {cls}")


if __name__ == "__main__":
    main()