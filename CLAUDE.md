# Силовой дневник — репозиторий

Исходник опубликованного Artifact «Силовой дневник» + резервные выгрузки его базы данных.
Владелец: Alex (Вильнюс). Язык общения — русский, максимально плотно.

## Идентификаторы
- URL: https://claude.ai/artifact/TefgCATmkGnFEom2G5mCXo
- slug (UUID, для db_* и publish): `d7cff59c-52a8-447e-9b32-224353e0d346`
- runtime-контракт: 0.2.87; capabilities страницы: `db`, `assets`, `user`
- `.published-version` — id последней опубликованной из этого репозитория версии

## Что где
- `diary.html` — **полный** документ страницы (`<!doctype html>…<body>` + тело + `</body></html>`). Единственный источник кода.
- `data/exercises.json` — выгрузка коллекции `exercises` (массив `{id,data,version,updatedAt}`, по `id`).
- `data/log/ГГГГ-ММ-ДД.json` — выгрузка одного дня коллекции `log` (имя файла — ISO-дата; `id` документа в формате `ДД-ММ-ГГГГ` внутри).
- `tools/verify_export.py` — проверка выгрузки.

## Правка и публикация кода
1. `get_artifact(slug)` → сверить `version` с `.published-version`. Если отличается — страницу правили вне репозитория: `read_artifact`, свести различия в `diary.html`, только потом править.
2. Править `diary.html` точечно. Проверка: `python3 -c` вынуть `<script>…</script>` в файл → `node --check`.
3. Публикация: `publish_files(slug, base_version=<live>, files=[{as:"index.html", path:"diary.html"}])` (перед первой публикацией за сессию — `guide(topic="pages")`). Данные базы публикация не затрагивает.
4. Записать новый `version` в `.published-version`, коммит.

## Схема базы (не ломать совместимость)
- `exercises/{id}`: `days[]` (mon..sun), `order`, `name`, `block`, `target`, `note`, `active`, `photo` (первое фото), `photos[]` (до 3 asset-id; сервятся как `/_blob/<id>`), `technique`, `mode` (`"check"` — только кнопка «Выполнено», без подходов).
- `log/{ДД-ММ-ГГГГ}`: `date` (ДД.ММ.ГГГГ), `entries{ id:{sets,reps,perSet?} }`, `updatedAt`.
  - одинаковые подходы: `{sets,reps}`; разные: `{sets,reps(среднее),perSet:[…]}`; `mode:"check"` пишется как `{sets:1,reps:1}`; у упражнений на время `reps` — отметка, не повторы.
  - в логе бывают выключенные (`active:false`) и внеплановые упражнения — это нормально.
- **Удаления в базе необратимы.** `log` не писать и не удалять без прямой просьбы Alex; `exercises` — только по согласию.

## Выгрузка базы (по расписанию и по запросу)
1. `db_list(slug,"exercises",limit=1000)` и `db_list(slug,"log",limit=1000)`; если `nextCursor` не пуст — дочитать.
2. Записать `data/exercises.json` и по файлу на день в `data/log/` **дословно** (не переформулировать тексты, не «чинить» данные; сортировка по `id`; JSON `ensure_ascii=False`, отступ 1).
3. `python3 tools/verify_export.py --exercises N --log M` (N, M — `count` из db_list). Расхождение — не коммитить, разобраться.
4. Нет изменений (`git diff --quiet`) → ничего не коммитить. Иначе коммит `export: ГГГГ-ММ-ДД, N упр., M дней` и push.
5. Документы с `tooLarge` (данных нет) — не выдумывать, перечислить в сообщении коммита.

## Восстановление из выгрузки
`db_write` по документам из JSON (по одному, `id` и `data` как в файле). Фото-ассеты в выгрузку не входят (в базе только их id).

## Безопасность
Репозиторий приватный. Ключи, токены, пароли не хранить и не выводить.
