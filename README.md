# strength-diary

Силовой дневник Alex: исходник страницы (Claude Artifact) и резервные выгрузки её базы.

- Работающая страница: https://claude.ai/artifact/TefgCATmkGnFEom2G5mCXo — данные хранятся в базе артефакта (облако claude.ai), здесь — снимки.
- Код: `diary.html`. Правки и публикация — через Claude Code, процедура в `CLAUDE.md`.
- Данные: `data/exercises.json`, `data/log/ГГГГ-ММ-ДД.json`; выгрузка по расписанию, проверка — `tools/verify_export.py`.
- Данные, внесённые после последней выгрузки, существуют только в облаке.
