# Аппаратные платформы UserGate — пакет данных

Дата сбора: 2026-11-21. Источник: портал документации UserGate, раздел «Аппаратные платформы». Для каждой платформы сохранены оригиналы PDF, извлечённый Markdown и метаданные.

## Состав

| Продукт | Документов | Страниц | OCR-черновики | Папка |
|---|---:|---:|---:|---|
| UserGate B50 | 3 | 43 | 1 | [`usergate-b50`](usergate-b50/README.md) |
| UserGate C100 | 2 | 17 | 1 | [`usergate-c100`](usergate-c100/README.md) |
| UserGate C150 | 3 | 32 | 1 | [`usergate-c150`](usergate-c150/README.md) |
| UserGate C151 | 3 | 44 | 1 | [`usergate-c151`](usergate-c151/README.md) |
| UserGate D200, D500 | 4 | 45 | 2 | [`usergate-d200-d500`](usergate-d200-d500/README.md) |
| UserGate D250 | 3 | 44 | 1 | [`usergate-d250`](usergate-d250/README.md) |
| UserGate E1000, E3000 | 6 | 61 | 2 | [`usergate-e1000-e3000`](usergate-e1000-e3000/README.md) |
| UserGate E1010, E3010 | 5 | 45 | 2 | [`usergate-e1010-e3010`](usergate-e1010-e3010/README.md) |
| UserGate F8000 | 4 | 36 | 1 | [`usergate-f8000`](usergate-f8000/README.md) |
| UserGate F8010 | 4 | 37 | 1 | [`usergate-f8010`](usergate-f8010/README.md) |
| UserGate FG | 3 | 37 | 1 | [`usergate-fg`](usergate-fg/README.md) |
| UserGate X1 | 3 | 9 | 0 | [`usergate-x1`](usergate-x1/README.md) |

## Качество

- Всего документов: 43; страниц: 450.
- OCR-черновиков: 14 — это datasheet'ы без текстового слоя (в основном 15-страничные брошюры).
- Документы с текстовым слоем (руководства по эксплуатации, IPMI, рельсы, замена дисков, обновление ПО) извлечены `pypdf` без OCR.
- OCR-текст **не вычитан по страницам**: возможны ошибки в числах, латинице и названиях. Для точных характеристик используйте руководство по эксплуатации (там таблицы с текстовым слоем) или PDF из `source/`.
- Datasheet X10 разобран отдельно и вычитан вручную: [`usergate-x10`](usergate-x10/README.md).

## Как использовать

Индексировать `parsed/*.md`. PDF и Markdown одновременно не класть — будут дубли. Метаданные: `metadata/documents.json`, `metadata/sources.csv`, постраничный текст: `metadata/pages.jsonl`.
