#!/usr/bin/env python3
# coding: utf-8
import re
import collections
from pathlib import Path
import sys

TRIPLE_RE = re.compile(r'^\(.+?,\s*type\s*,\s*(.+?)\)$')

def main(path: str) -> None:
    cls_counter = collections.Counter()

    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            m = TRIPLE_RE.match(line.strip())
            if m:
                cls_counter[m.group(1)] += 1

    # 👉 вывод
    print(f'🔢 Всего различных классов: {len(cls_counter)}\n')
    print('📊 Частоты по классам:')
    for cls, cnt in cls_counter.most_common():
        print(f'  {cls:30} — {cnt}')

if __name__ == '__main__':
    main(sys.argv[1])
