"""Проверка базы знаний Partner-Agent перед сборкой индекса.

    python tools/data_audit.py              # структура, JSON, мусор, сущности
    python tools/data_audit.py --check-urls # ещё и доступность URL из urls.txt

Скрипт ничего не меняет: только читает `data/company/` и печатает отчёт.
Возвращает 0, если критичных ошибок нет, и 1, если есть.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from partner.domain.loaders import build_knowledge  # noqa: E402

COMPANY = ROOT / "data" / "company"

# Обрывки поисковой выдачи, которые не должны попадать в индекс.
# README.md в корне компания-папки не индексируется и служит местом для пометок.
FORBIDDEN_PATTERNS = (
    re.compile(r"(?i)krayon\.ru"),
    re.compile(r"(?i)abrikos-group\.ru"),
    re.compile(r"(?i)\b[a-z0-9-]+\.[a-z]{2,}\s+\+\d\b"),
)

REQUIRED_FILES = ("profile.json", "agent.json", "urls.txt")


def human(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def check_json(errors: list[str]) -> tuple[dict, dict]:
    profile: dict = {}
    agent: dict = {}
    for name in ("profile.json", "agent.json"):
        path = COMPANY / name
        if not path.is_file():
            errors.append(f"нет файла {human(path)}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{human(path)}: невалидный JSON — {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{human(path)}: ожидался объект JSON")
            continue
        if name == "profile.json":
            profile = payload
        else:
            agent = payload
    return profile, agent


def check_profile(profile: dict, errors: list[str], warnings: list[str]) -> None:
    if not profile:
        return
    for key in ("name", "description", "products", "contacts"):
        if not profile.get(key):
            warnings.append(f"profile.json: пустое поле «{key}»")
    products = profile.get("products") or []
    if products and not isinstance(products, list):
        errors.append("profile.json: products должен быть списком")
    contacts = profile.get("contacts")
    if contacts and not isinstance(contacts, dict):
        errors.append("profile.json: contacts должен быть объектом")


def check_agent(agent: dict, errors: list[str], warnings: list[str]) -> None:
    if not agent:
        return
    if not agent.get("rules"):
        warnings.append("agent.json: нет блока rules — правила поведения не заданы")
    if not agent.get("fallback"):
        warnings.append("agent.json: нет fallback — при отсутствии данных ответ будет пустым")
    glossary = agent.get("glossary")
    if glossary and not isinstance(glossary, dict):
        errors.append("agent.json: glossary должен быть объектом")


def scan_files(errors: list[str], warnings: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not COMPANY.is_dir():
        errors.append("нет каталога data/company")
        return counts
    for path in sorted(COMPANY.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        folder = path.relative_to(COMPANY).parts[0] if len(path.relative_to(COMPANY).parts) > 1 else ""
        counts[folder or "корень"] = counts.get(folder or "корень", 0) + 1
        # README в корне — инструкция для людей, в индекс не попадает.
        indexed = path != COMPANY / "README.md"
        if path.suffix.lower() not in {".md", ".txt", ".json", ".pdf", ".docx", ".html", ".csv"}:
            warnings.append(f"{human(path)}: формат не индексируется")
            continue
        if not indexed or path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                errors.append(f"{human(path)}: найден артефакт поисковой выдачи «{pattern.pattern}»")
        if len(text) < 40:
            warnings.append(f"{human(path)}: слишком короткий текст, будет пропущен")
    return counts


def build(errors: list[str]) -> dict:
    try:
        knowledge = build_knowledge(ROOT / "data", fetch_web=False, progress=None)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"сборка знаний упала: {type(exc).__name__}: {exc}")
        return {}
    entities = knowledge.entities
    return {
        "документов": len(knowledge.documents),
        "продуктов": len(entities.products),
        "людей": len(entities.people),
        "FAQ": len(entities.faq),
        "новостей": len(entities.news),
        "ошибок источников": len(knowledge.report.get("errors") or []),
        "пропущено файлов": knowledge.report.get("skipped", 0),
        "компания": entities.company.get("name") or "—",
        "документы": knowledge.documents,
    }


def check_urls(urls: list[str], errors: list[str], warnings: list[str]) -> None:
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError as exc:
        warnings.append(f"проверка URL пропущена: {exc}")
        return
    with httpx.Client(timeout=30, follow_redirects=True,
                      headers={"User-Agent": "PartnerAgent/0.1 (+knowledge base)"}) as client:
        for url in urls:
            try:
                response = client.get(url)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{url}: не открылась ({type(exc).__name__})")
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            size = len(" ".join(soup.get_text(" ", strip=True).split()))
            status = "ок" if size >= 200 else "мало текста"
            if size < 200:
                warnings.append(f"{url}: всего {size} символов текста")
            print(f"  {response.status_code}  {size:>7}c  {status:14} {url}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Проверка базы знаний")
    parser.add_argument("--check-urls", action="store_true", help="проверить доступность URL")
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []

    print("=" * 70)
    print(f"База знаний: {human(COMPANY)}")
    print("=" * 70)

    for name in REQUIRED_FILES:
        if not (COMPANY / name).is_file():
            errors.append(f"нет обязательного файла {name}")

    profile, agent = check_json(errors)
    check_profile(profile, errors, warnings)
    check_agent(agent, errors, warnings)
    counts = scan_files(errors, warnings)

    print("\nФайлы по папкам:")
    for folder, count in sorted(counts.items()):
        print(f"  {folder:12} {count}")

    knowledge = build(errors)
    urls: list[str] = []
    urls_file = COMPANY / "urls.txt"
    if urls_file.is_file():
        urls = [
            line.strip() for line in urls_file.read_text(encoding="utf-8-sig").splitlines()
            if line.strip().startswith(("http://", "https://"))
        ]

    if knowledge:
        print("\nРазбор материалов:")
        for key, value in knowledge.items():
            if key == "документы":
                continue
            print(f"  {key:22} {value}")

        kinds: dict[str, int] = {}
        for document in knowledge["документы"]:
            kinds[document.kind] = kinds.get(document.kind, 0) + 1
        print("\nТипы документов:")
        for kind, count in sorted(kinds.items()):
            print(f"  {kind:12} {count}")

        if not knowledge["продуктов"]:
            warnings.append("в базе нет ни одного продукта — проверьте папку products/")
        if not knowledge["FAQ"]:
            warnings.append("в базе нет ни одной пары вопрос/ответ — проверьте формат Q:/A:")

    print(f"\nURL в urls.txt: {len(urls)}")
    if args.check_urls and urls:
        print("\nПроверка URL:")
        check_urls(urls, errors, warnings)

    if warnings:
        print("\nПредупреждения:")
        for item in warnings:
            print(f"  ! {item}")

    print()
    if errors:
        print("Ошибки:")
        for item in errors:
            print(f"  × {item}")
        print(f"\nИтого: {len(errors)} ошибок, {len(warnings)} предупреждений")
        return 1

    print(f"Итого: ошибок нет, {len(warnings)} предупреждений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
