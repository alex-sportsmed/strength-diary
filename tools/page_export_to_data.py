#!/usr/bin/env python3
"""Раскладка файла, скачанного кнопкой «Экспорт JSON» на странице (побайтно точная выгрузка), в data/.
Использование: python3 -I tools/page_export_to_data.py ФАЙЛ.json
Формат файла: {exportedAt, collections:{имя:[{id,data}]}}. Версии и updatedAt документов страница не отдаёт:
для неизменившихся документов они берутся из прежнего файла, для изменившихся — не пишутся.
Полный снимок: файлы, которых нет в выгрузке, удаляются.
"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
LAYOUT = [("exercises", "single", None), ("log", "dir", "iso")]

def dump(o): return json.dumps(o, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

def merge(doc, old):
    if old and old.get("data") == doc["data"]:
        doc = {**doc, **{k: old[k] for k in ("version", "updatedAt") if k in old}}
    return doc

def iso(i):
    dd, mm, yy = i.split("-"); return f"{yy}-{mm}-{dd}"

src = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf8"))
cols = src["collections"]
(root / "data").mkdir(exist_ok=True)
counts = {}
for name, kind, namer in LAYOUT:
    docs = sorted(cols[name], key=lambda d: d["id"])
    counts[name] = len(docs)
    if kind == "single":
        f = root / "data" / (name + ".json")
        old = {d["id"]: d for d in json.loads(f.read_text(encoding="utf8"))} if f.exists() else {}
        f.write_text(dump([merge(d, old.get(d["id"])) for d in docs]), encoding="utf8")
    else:
        d_ = root / "data" / name; d_.mkdir(parents=True, exist_ok=True); keep = set()
        for d in docs:
            fn = eval(namer)(d["id"]) + ".json"; keep.add(fn); f = d_ / fn
            old = json.loads(f.read_text(encoding="utf8")) if f.exists() else None
            f.write_text(dump(merge(d, old)), encoding="utf8")
        for f in d_.glob("*.json"):
            if f.name not in keep: f.unlink()
print(" ".join(f"{k}={v}" for k, v in counts.items()))
