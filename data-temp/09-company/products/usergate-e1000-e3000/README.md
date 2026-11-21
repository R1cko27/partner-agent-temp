# UserGate E1000, E3000 — материалы для RAG

Страница документации: [UserGate E1000, E3000](https://docs.usergate.com/usergate-e1000-e3000_626.html). Скачано 2026-11-21.

## Документы

| Документ | Страниц | Версия / дата | Извлечение | Markdown |
|---|---:|---|---|---|
| Технические характеристики UserGate E1000 | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-e1000-datasheet-ru.md`](parsed/usergate-e1000-datasheet-ru.md) |
| Технические характеристики UserGate E3000 | 15 | не указана / не указана | OCR, черновик | [`parsed/usergate-e3000-datasheet-ru.md`](parsed/usergate-e3000-datasheet-ru.md) |
| Руководство по эксплуатации | 14 | 7.x / 2025/10/20 | текстовый слой | [`parsed/instruction-usergate-e.md`](parsed/instruction-usergate-e.md) |
| Удаленное управление с помощью IPMI | 4 | 7.x / 2026/05/04 | текстовый слой | [`parsed/instruction-usergate-ipmi.md`](parsed/instruction-usergate-ipmi.md) |
| Инструкция по установке рельс в стойку | 2 | не указана / не указана | текстовый слой | [`parsed/instruction-usergate-e-f.md`](parsed/instruction-usergate-e-f.md) |
| Инструкция по замене дисков на платформах E1000, E3000 | 11 | 7.x / 2025/09/01 | текстовый слой | [`parsed/usergate-e-drives-replace.md`](parsed/usergate-e-drives-replace.md) |

## Качество

- Документов без текстового слоя: 2. Текст получен OCR и **не вычитан по страницам**. Возможны ошибки в числах, латинице и названиях. Для точных характеристик сверяйтесь с PDF в `source/`.
- Таблицы в текстовых PDF сохранены в layout-виде: колонки могут быть разделены пробелами, но значения не потеряны.
- Общие документы (обновление через PMC, IPMI, рельсы) продублированы в папках продуктов, к которым они относятся.

## Как использовать

Основной материал — файлы в `parsed/`. Метаданные и постраничный текст — в `metadata/`. Папка лежит в `data-temp/`, поэтому в индекс автоматически не попадает.

```powershell
Copy-Item data-temp\09-company\products\usergate-e1000-e3000\parsed\*.md data\company\products\
python ingest.py --incremental
```

Не кладите в индекс одновременно PDF и его Markdown-разбор: будут дубли.
