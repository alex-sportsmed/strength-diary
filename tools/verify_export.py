#!/usr/bin/env python3
"""Проверка выгрузки силового дневника.
Использование: python3 -I tools/verify_export.py --exercises N --log M
Выход 0 — всё сходится; 1 — есть ошибки.
"""
import argparse, json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--exercises", type=int, required=True)
ap.add_argument("--log", type=int, required=True)
a = ap.parse_args()

err, warn = [], []

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        err.append(f"{p.relative_to(root)}: не JSON ({e})")
        return None

ex = load(root / "data" / "exercises.json") or []
ids = [d.get("id") for d in ex]
if len(ex) != a.exercises:
    err.append(f"exercises: в файле {len(ex)}, ожидалось {a.exercises}")
if len(set(ids)) != len(ids):
    err.append("exercises: дубли id")
if ids != sorted(ids):
    warn.append("exercises: не отсортировано по id")
for d in ex:
    for k in ("id", "data", "version", "updatedAt"):
        if k not in d:
            err.append(f"exercises/{d.get('id')}: нет поля {k}")
    dd = d.get("data", {})
    for k in ("name", "days", "order", "active"):
        if k not in dd:
            err.append(f"exercises/{d.get('id')}: нет data.{k}")

files = sorted((root / "data" / "log").glob("*.json"))
if len(files) != a.log:
    err.append(f"log: файлов {len(files)}, ожидалось {a.log}")
known = set(ids)
for f in files:
    d = load(f)
    if d is None:
        continue
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.stem):
        err.append(f"{f.name}: имя не ГГГГ-ММ-ДД")
        continue
    y, m, dn = f.stem.split("-")
    if d.get("id") != f"{dn}-{m}-{y}":
        err.append(f"{f.name}: id={d.get('id')} не соответствует имени")
    data = d.get("data", {})
    if data.get("date") != f"{dn}.{m}.{y}":
        err.append(f"{f.name}: data.date={data.get('date')}")
    for eid, en in data.get("entries", {}).items():
        if eid not in known:
            warn.append(f"{f.name}: упражнение {eid} нет в каталоге (удалено?)")
        if not isinstance(en.get("sets"), (int, float)) or not isinstance(en.get("reps"), (int, float)):
            err.append(f"{f.name}/{eid}: sets/reps не числа")
        pr = en.get("perSet")
        if pr is not None and len(pr) != en.get("sets"):
            err.append(f"{f.name}/{eid}: len(perSet)={len(pr)} != sets={en.get('sets')}")

for w in warn:
    print("WARN", w)
for e in err:
    print("ERR ", e)
print(f"exercises={len(ex)} log={len(files)} errors={len(err)} warnings={len(warn)}")
sys.exit(1 if err else 0)
