# UserGate E1010, E3010 — материалы для RAG

Страница документации: [UserGate E1010, E3010](https://docs.usergate.com/usergate-e1010-e3010_3160.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики UserGate E1010 | 8 | не указана / не указана | OCR, черновик | [`parsed/usergate-ngfw-e1010-datasheet-ru.md`](parsed/usergate-ngfw-e1010-datasheet-ru.md) |
| Технические характеристики UserGate E3010 | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-ngfw-e3010-datasheet-ru.md`](parsed/usergate-ngfw-e3010-datasheet-ru.md) |
| Руководство по эксплуатации | 15 | 7.x / 2026/03/19 | текстовый слой | [`parsed/instruction-usergate-e1010-e3010.md`](parsed/instruction-usergate-e1010-e3010.md) |
| Удаленное управление с помощью IPMI | 5 | не указана / не указана | текстовый слой | [`parsed/instruction-usergate-ipmi-amd.md`](parsed/instruction-usergate-ipmi-amd.md) |
| Инструкция по установке рельс в стойку | 2 | не указана / не указана | текстовый слой | [`parsed/instruction-usergate-e-f.md`](parsed/instruction-usergate-e-f.md) |

## Качество

- Документов без текстового слоя: 2. Текст получен OCR и **не вычитан по страницам**. Возможны ошибки в числах, латинице и названиях. Для точных характеристик сверяйтесь с PDF в `source/`.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-e1010-e3010\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
