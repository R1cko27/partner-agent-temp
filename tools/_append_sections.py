"""Дополняет карточки продуктов проверенными по базе разделами."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = pathlib.Path("data/company/products")

BLOCKS = {
    "waf.md": """
## Версии и сертификация

В портале документации на 2026-11-20 у UserGate WAF указаны версии **7.6.x и 7.7.x**: для каждой есть руководство администратора (7.6.x RU, 7.7.x RU) и отдельное описание API 7.7.0 EN. В таблице совместимости с аппаратными платформами фигурирует версия 7.6.0 — доступность конкретной версии зависит от модели платформы, поэтому перед обновлением сверяются с таблицей совместимости.

Модуль защиты от веб-уязвимостей на странице продукта назван «OWASP Top-10»: SQL-инъекции, межсайтовый скриптинг, подделка межсайтовых запросов, инъекции команд.

В Академии UserGate есть отдельный экзамен «Сертифицированный специалист UserGate WAF 7.Х» — он подтверждает подготовку именно по защите веб-приложений, а не по всей линейке продуктов.

Источники: https://docs.usergate.com/dokumentaciya-k-versiyam-po-v-pdf_769.html, https://usergate.com/academy/courses-exams
""",
    "dcfw.md": """
## Кластеры и отказоустойчивость

UserGate DCFW поддерживает **два типа кластеров**: кластер конфигурации, который задаёт единые настройки узлам в рамках кластера, и кластер отказоустойчивости, который обеспечивает резервирование. Кластер отказоустойчивости объединяет до **четырёх узлов** кластера конфигурации и работает в режиме «активный-активный» или «активный-пассивный»; таких кластеров можно собрать несколько.

Служебный трафик кластера передаётся по multicast или unicast, узлы идентифицируются по VRID. Для служебных пакетов VRRP в кластере отказоустойчивости поддерживается **подпись IPsec Authentication Header**: параметр `auth-type` включает подпись служебных пакетов.

Часть параметров остаётся уникальной для каждого узла и не реплицируется: Log Analyzer, диагностика, интерфейсы, шлюзы, DHCP, маршруты, OSPF и BGP.

Мониторинг поддерживается по SNMP v2c и SNMP v3 — как запросы (queries), так и оповещения (traps).

Источники: https://docs.usergate.com/klasterizaciya-i-otkazoustojchivost6_1605.html, https://docs.usergate.com/funkcional6nye-vozmozhnosti_2248.html
""",
    "log-analyzer.md": """
## Журналы, агент UserID и передача событий

Log Analyzer собирает журналы устройств, хранит и обрабатывает их, а также передаёт события в UserGate SIEM.

Агент UserID периодически опрашивает настроенные источники и складывает события в служебную базу. В журналах видны его служебные события: `server_added` и `server_delete_failed` (добавление и удаление сервера), `filter_added` и `filter_updated` (Syslog-фильтры), `set_agent_config` и `set_agent_config_failed` (настройки агента), `sharing_profile_added` и `sharing_profile_add_failed` (профили редистрибуции). По ним проверяют, работает ли сбор данных о пользователях.

Syslog-фильтры агента настраиваются в разделе «Библиотеки → Syslog фильтры UserID агента». Для поиска информации о найденных пользователях используется LDAP-коннектор: в разделе «Пользователи и устройства» выбирается каталог, по которому агент сопоставляет логины из журналов.

События передаются по syslog в форматах RFC 3164, 5424 и 6587.

Источники: https://docs.usergate.com/pol6zovateli-i-ustrojstva-623/
""",
    "swg.md": """
## Captive-портал, WCCP и сетевые функции

В UserGate SWG настраиваются служебные домены для входа пользователей через **captive-портал** и выхода из сессии: шаблоны страниц авторизации есть на русском и английском языках.

Перенаправление трафика на прокси-службы поддерживается по **WCCP** (Web Cache Communication Protocol).

Сетевые функции включают статическую и динамическую маршрутизацию, поддержку **VLAN**, трансляцию адресов, VPN-туннели и механизмы аутентификации пользователей (Captive-портал, SAML, LDAP-коннекторы, агент UserID).

Источники: документация SWG на https://docs.usergate.com/
""",
}


def main() -> int:
    changed = 0
    for name, extra in BLOCKS.items():
        path = BASE / name
        if not path.is_file():
            print("нет файла:", name)
            continue
        text = path.read_text(encoding="utf-8")
        marker = extra.strip().splitlines()[0]
        if marker in text:
            print("уже есть:", name)
            continue
        path.write_text(text.rstrip() + "\n" + extra, encoding="utf-8")
        changed += 1
        print(f"дополнено: {name} · {len(text)} -> {len(text) + len(extra)} символов")
    print("изменено файлов:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
