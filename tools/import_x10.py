"""Переносит материалы UserGate X10 из data-temp в базу знаний.

1. Три разобранных документа → data/company/docs/hardware/ с шапкой источника.
2. Карточка продукта → data/company/products/usergate-x10.md.
3. Оригиналы PDF остаются в data-temp (в индекс не идут).
"""

from __future__ import annotations

import io
import pathlib
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = pathlib.Path("data-temp/09-company/products/usergate-x10")
DATA = pathlib.Path("data/company")
DOCS = DATA / "docs" / "hardware"
PRODUCTS = DATA / "products"

DOCUMENTS = (
    (
        "parsed/01-datasheet-usergate-x10.md",
        "01-x10-datasheet.md",
        {
            "заголовок": "UserGate NGFW X10 — технические характеристики (datasheet)",
            "url": "https://static.usergate.com/docs/overviews/usergate-x10-datasheet-ru.pdf",
            "источник": "static.usergate.com (PDF, 15 страниц, OCR)",
            "продукт": "X10",
            "версия": "не указана (измерения на NGFW 7.5)",
            "раздел": "Аппаратные платформы",
            "обновлено": "2026-09-01",
        },
    ),
    (
        "parsed/02-instruction-usergate-x10.md",
        "02-x10-instruction.md",
        {
            "заголовок": "UserGate X10 — руководство по эксплуатации",
            "url": "https://docs.usergate.com/hardware/instruction-usergate-x10.pdf",
            "источник": "docs.usergate.com (PDF, 16 страниц)",
            "продукт": "X10",
            "версия": "7.x",
            "раздел": "Аппаратные платформы",
            "обновлено": "2026-08-19",
        },
    ),
    (
        "parsed/03-sw-update-over-pmc.md",
        "03-x10-sw-update-pmc.md",
        {
            "заголовок": "Обновление компонентов ПО через PMC (аппаратные платформы UserGate)",
            "url": "https://docs.usergate.com/hardware/sw-update-over-pmc.pdf",
            "источник": "docs.usergate.com (PDF, 15 страниц)",
            "продукт": "X10",
            "версия": "7.x",
            "раздел": "Аппаратные платформы",
            "обновлено": "2026-07-08",
        },
    ),
)

CARD = """# UserGate NGFW X10

Аппаратный межсетевой экран нового поколения для защиты объектов АСУ ТП и работы в экстремальных условиях: пассивное охлаждение, монтаж на DIN-рейку, диапазон температур от −40 до +60 °C.

## Назначение

Небольшие организации и филиалы, технологические сети (АСУ ТП): подстанции, буровые, производственные цеха, диспетчерские пункты.

## Условия эксплуатации

- температура от **−40 до +60 °C**, относительная влажность до 80%;
- пассивное охлаждение, вентиляторов нет;
- защита от пыли на уровне **IP30**, монтаж на DIN-рейку;
- питание: один внешний блок 12 В, сеть 100–240 В, потребление 24 Вт;
- поддержка до двух блоков питания AC/DC или DC/DC.

## Аппаратная конфигурация

| Параметр | Значение |
|---|---|
| Процессор | 1 × ARM, 4 ядра, 4 потока, 1,8 ГГц |
| Память | 16 ГБ DDR4 |
| Накопитель | SSD 128 ГБ |
| Порты данных | 6 × RJ-45 (1 пара с bypass), 1 × SFP+ |
| Служебные порты | RJ-45 и USB Type-C для PMC, USB 3.0 Type-A |
| Слоты NIC | нет |

## Производительность (измерения на NGFW 7.5)

| Параметр | Значение |
|---|---:|
| FW L4, UDP 1500 байт | 3 500 Мбит/с |
| FW L4, EMIX | 1 800 Мбит/с |
| FW L4, новые сессии | 7 500 CPS |
| FW L4, сессии TCP | 1 500 000 |
| FW L7, EMIX | 950 Мбит/с |
| FW L7, новые сессии | 3 500 CPS |
| FW L7 + IPS, EMIX | 100 Мбит/с |
| FW L7 + CF, HTTP | 250 Мбит/с |
| FW L7 + CF, HTTPS (TLSv1.2) | 100 Мбит/с |
| NGFW (L7 + IPS + CF), EMIX | 40 Мбит/с |

## Функции

Контроль состояния сессий, контроль приложений, трансляция адресов, предотвращение вторжений, контентная фильтрация, идентификация пользователей (UserID), защита от вирусов, спама и фишинга, дешифрование SSL, шифрование канала связи, защищённый удалённый доступ, защита от DoS-атак.

## Сертификация

- ФСТЭК России: 4-й уровень доверия, требования к МЭ по профилю защиты А, Б и Д 4-го класса, СОВ уровня сети 4-го класса — **сертификат № 3905**;
- реестр Минцифры России;
- декларации о соответствии техническим регламентам;
- отдельно — сертификаты ОАЦ Республики Беларусь и ОАО «Гипросвязь».

Важно: номер 3905 относится к решению NGFW; переносить его на другие продукты нельзя.

## Подписки

Security Updates (SU), Advanced Threat Protection (ATP), Stream Antivirus, Mail Security.

## Материалы в базе

- `docs/hardware/01-x10-datasheet.md` — технические характеристики и возможности;
- `docs/hardware/02-x10-instruction.md` — руководство по эксплуатации: панели, установка, обслуживание, первоначальная настройка;
- `docs/hardware/03-x10-sw-update-pmc.md` — обновление ПО через PMC по TFTP/SCP, переустановка UGOS через sys-recovery, сертификат SSH.

Источники: https://docs.usergate.com/usergate-x10_3226.html, https://static.usergate.com/docs/overviews/usergate-x10-datasheet-ru.pdf, https://docs.usergate.com/hardware/instruction-usergate-x10.pdf
"""


def front_matter(meta: dict) -> str:
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.append("получено: 2026-11-21")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)

    for source_rel, target_name, meta in DOCUMENTS:
        source = SRC / source_rel
        if not source.is_file():
            print("нет файла:", source)
            continue
        body = source.read_text(encoding="utf-8").strip()
        target = DOCS / target_name
        # Шапку из parsed-файла заменяем своей, чтобы в индексе были URL и дата.
        if body.startswith("# "):
            heading, _, rest = body.partition("\n")
            body = f"{heading}\n{rest}"
        target.write_text(front_matter(meta) + "\n\n" + body + "\n", encoding="utf-8")
        print(f"документ: {target.relative_to(DATA)} · {len(body)} символов")

    card = PRODUCTS / "usergate-x10.md"
    card.write_text(CARD, encoding="utf-8")
    print(f"карточка: {card.relative_to(DATA)} · {len(CARD)} символов")

    # Оригиналы PDF оставляем в data-temp, но фиксируем их наличие
    pdfs = list((SRC / "source").glob("*.pdf"))
    print("PDF в data-temp (в индекс не идут):", len(pdfs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
