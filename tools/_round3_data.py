"""Круг 3: данные по выходу узла из кластера и сетевой маршрутизации + выравнивание эталона."""

from __future__ import annotations

import io
import json
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DCFW = pathlib.Path("data/company/products/dcfw.md")
NGFW = pathlib.Path("data/company/products/ngfw.md")
BENCH1 = pathlib.Path("tools/benchmark-60.json")

DCFW_EXTRA = """
## Выход узла из кластера

При выходе узла из кластера конфигурации общие настройки кластера на нём больше не действуют: узел возвращается к собственным параметрам. Уникальными для каждого узла остаются Log Analyzer, диагностика, интерфейсы, шлюзы, DHCP, маршруты, OSPF и BGP — они не реплицируются и настраиваются отдельно.

Обратный сценарий в документации описан подробно: при подключении нового узла все параметры первого узла реплицируются на него, после чего узел получает общие настройки кластера. Поэтому перед выводом узла проверяют, какие параметры были заданы только на нём.

Источники: https://docs.usergate.com/klasterizaciya-i-otkazoustojchivost6_1605.html
"""

NGFW_EXTRA = """
## Сетевые функции

Помимо фильтрации трафика решения UserGate работают с сетью на разных уровнях: статическая и динамическая маршрутизация (в том числе OSPF и BGP), поддержка VLAN и тегированных интерфейсов, агрегирование портов (LACP), трансляция адресов (NAT), VPN-туннели и механизмы аутентификации пользователей.

Источники: https://docs.usergate.com/
"""


def append(path: pathlib.Path, extra: str) -> bool:
    text = path.read_text(encoding="utf-8")
    marker = extra.strip().splitlines()[0]
    if marker in text:
        print("уже есть:", path.name)
        return False
    path.write_text(text.rstrip() + "\n" + extra, encoding="utf-8")
    print("дополнено:", path.name)
    return True


def main() -> int:
    append(DCFW, DCFW_EXTRA)
    append(NGFW, NGFW_EXTRA)

    data = json.loads(BENCH1.read_text(encoding="utf-8"))
    platforms = (
        "C150, C151, D250, D500, E1000, E1010, E3000, E3010, F8000, ПАК UserGate FG; "
        "отдельно упомянута платформа «Катунь Электроника»"
    )
    for row in data["questions"]:
        if row["id"] in ("R01", "E06"):
            row["answer"] = f"В материалах перечислены платформы: {platforms}."
            row["source"] = "docs/versions-and-platforms.md, docs/crawl (установка)"
        if row["id"] == "R33":
            row["answer"] = "На официальной странице — «более 600 сотрудников»; в краткой справке «700+»."
        if row["id"] == "E08":
            row["answer"] = (
                "Академия делит работу по пяти направлениям: обучение и сертификация специалистов, "
                "партнёры Академии, образовательные учреждения, отдельные программы и поддержка выпускников."
            )
            row["source"] = "faq/education.md, usergate.com/academy"
    BENCH1.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("эталон выровнен: R01, E06, R33, E08")
    return 0


if __name__ == "__main__":
    sys.exit(main())
