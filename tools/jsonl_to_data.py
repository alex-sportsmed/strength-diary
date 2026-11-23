#!/usr/bin/env python3
"""Преобразует построчный вывод db_list в раскладку репозитория.
Использование: python3 -I tools/jsonl_to_data.py EXERCISES.jsonl LOG.jsonl
Каждая строка — один документ {data,id,updatedAt,version}, как её вернул db_list (без обёртки untrusted-document).
Пишет data/exercises.json и data/log/ГГГГ-ММ-ДД.json; лишние файлы дней удаляет (выгрузка — полный снимок).
"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent

def read(p):
    docs = []
    for i, line in enumerate(pathlib.Path(p).read_text(encoding="utf8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            docs.append(json.loads(line))
        except Exception as e:
            sys.exit(f"{p}:{i}: не JSON ({e})")
    return docs

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

ex = sorted(read(sys.argv[1]), key=lambda d: d["id"])
lg = read(sys.argv[2])
(root / "data").mkdir(exist_ok=True)
(root / "data" / "exercises.json").write_text(dump(ex), encoding="utf8")

logdir = root / "data" / "log"
logdir.mkdir(parents=True, exist_ok=True)
keep = set()
for d in lg:
    dd, mm, yy = d["id"].split("-")
    name = f"{yy}-{mm}-{dd}.json"
    keep.add(name)
    (logdir / name).write_text(dump(d), encoding="utf8")
for f in logdir.glob("*.json"):
    if f.name not in keep:
        f.unlink()
print(f"exercises={len(ex)} log={len(lg)}")
