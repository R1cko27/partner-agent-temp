# UserGate D200, D500 — материалы для RAG

Страница документации: [UserGate D200, D500](https://docs.usergate.com/usergate-d200-d500_625.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики UserGate D200 | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-d200-datasheet-ru.md`](parsed/usergate-d200-datasheet-ru.md) |
| Технические характеристики UserGate D500 | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-d500-datasheet-ru.md`](parsed/usergate-d500-datasheet-ru.md) |
| Руководство по эксплуатации | 11 | 7.x / 2025/10/20 | текстовый слой | [`parsed/instruction-usergate-d.md`](parsed/instruction-usergate-d.md) |
| Удаленное управление с помощью IPMI | 4 | 7.x / 2026/05/04 | текстовый слой | [`parsed/instruction-usergate-ipmi.md`](parsed/instruction-usergate-ipmi.md) |

## Качество

- Документов без текстового слоя: 2. Текст получен OCR и **не вычитан по страницам**. Возможны ошибки в числах, латинице и названиях. Для точных характеристик сверяйтесь с PDF в `source/`.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-d200-d500\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
