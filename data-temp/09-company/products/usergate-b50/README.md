# UserGate B50 — материалы для RAG

Страница документации: [UserGate B50](https://docs.usergate.com/usergate-b50_3164.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики UserGate B50-B | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-b50-datasheet-ru.md`](parsed/usergate-b50-datasheet-ru.md) |
| Руководство по эксплуатации UserGate B50-B | 13 | 7.x / 2026/07/27 | текстовый слой | [`parsed/instruction-usergate-b50-b.md`](parsed/instruction-usergate-b50-b.md) |
| Обновление компонентов ПО через PMC | 15 | 7.x / 2026/07/08 | текстовый слой | [`parsed/sw-update-over-pmc.md`](parsed/sw-update-over-pmc.md) |

## Качество

- Документов без текстового слоя: 1. Текст получен OCR и **не вычитан по страницам**. Возможны ошибки в числах, латинице и названиях. Для точных характеристик сверяйтесь с PDF в `source/`.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-b50\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
