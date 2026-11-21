# UserGate F8000 — материалы для RAG

Страница документации: [UserGate F8000](https://docs.usergate.com/usergate-f8000_627.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-f8000-datasheet-ru.md`](parsed/usergate-f8000-datasheet-ru.md) |
| Руководство по эксплуатации | 15 | 7.x / 2026/08/18 | текстовый слой | [`parsed/instruction-usergate-f.md`](parsed/instruction-usergate-f.md) |
| Удаленное управление с помощью IPMI | 4 | 7.x / 2026/05/04 | текстовый слой | [`parsed/instruction-usergate-ipmi.md`](parsed/instruction-usergate-ipmi.md) |
| Инструкция по установке рельс в стойку | 2 | не указана / не указана | текстовый слой | [`parsed/instruction-usergate-e-f.md`](parsed/instruction-usergate-e-f.md) |

## Качество

- Документов без текстового слоя: 1. Текст получен OCR и **не вычитан по страницам**. Возможны ошибки в числах, латинице и названиях. Для точных характеристик сверяйтесь с PDF в `source/`.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-f8000\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
