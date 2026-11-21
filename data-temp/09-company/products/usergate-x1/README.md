# UserGate X1 — материалы для RAG

Страница документации: [UserGate X1](https://docs.usergate.com/usergate-x1_628.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики | 3 | не указана / не указана | текстовый слой | [`parsed/usergate-x-datasheet-ru.md`](parsed/usergate-x-datasheet-ru.md) |
| Руководство по эксплуатации | 2 | не указана / не указана | текстовый слой | [`parsed/instruction-usergate-x.md`](parsed/instruction-usergate-x.md) |
| Удаленное управление с помощью IPMI | 4 | 7.x / 2026/05/04 | текстовый слой | [`parsed/instruction-usergate-ipmi.md`](parsed/instruction-usergate-ipmi.md) |

## Качество

- Все документы содержат текстовый слой; текст извлечён без OCR.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-x1\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
