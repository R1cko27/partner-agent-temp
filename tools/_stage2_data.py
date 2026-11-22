"""Этап 2: пополнение данных перед прогоном."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DATA = pathlib.Path("data/company")

BLOCKS = {
    "products/waf.md": """
## Версии 7.5.0

Кроме веток 7.6.x и 7.7.x, в материалах базы есть анонс версии **7.5.0** (отдельный документ о новой версии UserGate WAF 7.5.0). Полный перечень версий и руководств — в `docs/versions-and-platforms.md`.

В Академии UserGate есть экзамен **«Сертифицированный специалист UserGate WAF 7.Х»**; он подтверждает подготовку по защите веб-приложений, а не по всей линейке продуктов.

Источники: https://docs.usergate.com/dokumentaciya-k-versiyam-po-v-pdf_769.html, https://usergate.com/academy/courses-exams
""",
    "products/log-analyzer.md": """
## LDAP-коннектор и сопоставление логинов

**LDAP-коннектор сопоставляет логины из журналов с учётными записями пользователей**: в разделе «Пользователи и устройства» выбирается каталог, по которому агент UserID ищет информацию о найденных в журналах пользователях. Так события syslog превращаются в события конкретного человека, а не IP-адреса.

Источники: https://docs.usergate.com/pol6zovateli-i-ustrojstva-623/
""",
    "products/dcfw.md": """
## UserID: способы аутентификации

UserID — прозрачная аутентификация по журналам. Она не заменяет, а дополняет другие способы: **Captive-портал, NTLM, LDAP, Active Directory, RADIUS, SAML IDP**. В разделе «Пользователи и устройства» для каждого способа настраивается свой профиль, а UserID связывает сетевой адрес с именем пользователя.
""",
    "products/ngfw.md": """
## Масштаб внедрений и сетевые детали

В материалах компании есть формулировка **«более 7000 реализованных проектов»** (цитата из публикации о стратегии управляемой безопасности). Точного числа клиентов в базе нет.

Агрегирование портов по **LACP** повышает не только отказоустойчивость, но и **пропускную способность**: несколько физических линков работают как один логический канал. Наряду с тегированными VLAN поддерживаются **маршрутизация** (статическая и динамическая) и **трансляция адресов (NAT)**.
""",
    "products/client.md": """
## Совместимость и лицензирование

**Astra Linux — подтверждённая ОС** для UserGate Client: в материалах есть сообщение о совместимости uClient с Astra Linux, и функционал продолжает расширяться.

Лицензирование Client **по числу пользователей в открытых материалах не описано**: состав лицензии и расчёт по пользователям относятся к коммерческим условиям, их подтверждает sales@usergate.com.
""",
    "about/company.md": """
## Численность: две формулировки

На официальной странице «Работа в UserGate» указано **«более 600 сотрудников»**. В краткой справке партнёра фигурирует **«700+»** — это разные снимки данных. Называть одно число как точное нельзя: актуальное значение стоит сверять на сайте компании.

Источники: https://usergate.com/company/career, справка партнёра (архив 2026-11-20)
""",
    "faq/pricing.md": """
Q: Какой SLA у технической поддержки?
A: Условия SLA и сроки реагирования в открытых материалах не публикуются: они зависят от договора и уровня поддержки. Точные условия подтверждает sales@usergate.com.

Q: Какие сроки реакции у второй линии поддержки?
A: В материалах базы таких сроков нет. Ориентиры по SLA не публикуются — их согласуют с компанией индивидуально.
""",
}

ACADEMY = """# Академия UserGate

Обучение и сертификация по продуктам UserGate: курсы, экзамены, программы для вузов.

## Курсы и экзамены

Авторизованные курсы и сертификационные экзамены разработаны по пяти продуктам. В материалах упоминаются отдельные экзамены по NGFW, DCFW, WAF и SIEM, включая **«Сертифицированный специалист UserGate WAF 7.Х»**.

Стоимость: курсы — от 35 000 до 161 000 ₽, экзамены — от 9 000 до 17 500 ₽. Точную цену конкретной программы подтверждает academy@usergate.com.

## Программы для учебных заведений

Есть программа Educational Partnership: модули по решениям UserGate встраиваются в направления подготовки по ФГОС ВО, включая «Информационную безопасность» и ИКТ-направления.

## Адреса

- Каталог курсов и экзаменов: https://usergate.com/academy/courses-exams
- Академия: https://usergate.com/academy
- Портал документации: https://docs.usergate.com/
- Почта: academy@usergate.com

Источники: https://usergate.com/academy, https://usergate.com/academy/courses-exams, faq/education.md
"""


def append(name: str, block: str) -> None:
    path = DATA / name
    if not path.is_file():
        print("нет файла:", name)
        return
    text = path.read_text(encoding="utf-8")
    marker = block.strip().splitlines()[0]
    if marker in text:
        print("уже есть:", name)
        return
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    print("дополнено:", name)


def main() -> int:
    for name, block in BLOCKS.items():
        append(name, block)

    academy = DATA / "about" / "academy.md"
    if academy.is_file():
        print("academy.md уже есть")
    else:
        academy.write_text(ACADEMY, encoding="utf-8")
        print("создан: about/academy.md")

    channels = DATA / "about" / "official-channels.md"
    if channels.is_file():
        text = channels.read_text(encoding="utf-8")
        missing = [url for url in ("docs.usergate.com", "usergate.com/academy") if url not in text]
        if missing:
            text = text.rstrip() + (
                "\n\n## Дополнительно\n\n"
                "- Портал документации: https://docs.usergate.com/\n"
                "- Академия: https://usergate.com/academy\n"
            )
            channels.write_text(text, encoding="utf-8")
            print("official-channels: добавлены", ", ".join(missing))
        else:
            print("official-channels: адреса уже есть")
    return 0


if __name__ == "__main__":
    sys.exit(main())
