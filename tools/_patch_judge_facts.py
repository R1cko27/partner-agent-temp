"""Подключает реестр фактов к судье, а F07/F08 — к агенту."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

JUDGE = pathlib.Path("partner/engine/judge.py")
AGENT = pathlib.Path("partner/agent.py")


def patch_judge() -> None:
    text = JUDGE.read_text(encoding="utf-8")
    changed = []

    if "_load_facts" not in text:
        text = text.replace(
            "class Judge:\n    def __init__(self, client: DeepSeekClient, enabled: bool = True, max_tokens: int = 700) -> None:\n        self.client = client\n        self.enabled = enabled\n        self.max_tokens = max_tokens",
            '''class Judge:
    def __init__(
        self,
        client: DeepSeekClient,
        enabled: bool = True,
        max_tokens: int = 700,
        facts_path: Optional[Path] = None,
    ) -> None:
        self.client = client
        self.enabled = enabled
        self.max_tokens = max_tokens
        self._facts_path = facts_path or Path("storage/index/facts.json")
        self._facts: Dict[str, Any] = {}

    def _load_facts(self) -> Dict[str, Any]:
        """Реестр фактов базы: числа, версии, адреса, события."""
        if self._facts:
            return self._facts
        try:
            self._facts = json.loads(self._facts_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._facts = {}
        return self._facts

    def known_number(self, number: str) -> bool:
        facts = self._load_facts()
        return str(number) in (facts.get("numbers") or {})

    def known_url(self, url: str) -> bool:
        facts = self._load_facts()
        clean = str(url or "").rstrip(".,;")
        for key in (facts.get("urls") or {}):
            if clean == key or clean.rstrip("/") == key.rstrip("/"):
                return True
            if clean in key or key in clean:
                return True
        return False''',
        )
        changed.append("инициализация реестра")

    old_check = '''        if verdict == "invented":
            known = _normalize_numbers(reference + " " + context)
            unknown = [n for n in _numbers_in(answer) if n not in known]
            if not unknown:'''
    new_check = '''        if verdict == "invented":
            known = _normalize_numbers(reference + " " + context)
            # Реестр фактов базы: число может быть верным, но не попасть в контекст.
            unknown = [
                n for n in _numbers_in(answer)
                if n not in known and not self.known_number(n)
            ]
            if not unknown:'''
    if old_check in text:
        text = text.replace(old_check, new_check)
        changed.append("сверка чисел с реестром")

    if "from pathlib import Path" not in text:
        text = text.replace("import sys\n", "import sys\nfrom pathlib import Path\n", 1)
        changed.append("импорт Path")

    if changed:
        JUDGE.write_text(text, encoding="utf-8")
        print("судья:", ", ".join(changed))


def patch_agent() -> None:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    # F07: лицензии и кластер — карточки Management Center и DCFW
    old_hints = '    (("кластер", "отказоустойчив", "vrrp"), ("products/dcfw", "klasterizaciya")),'
    new_hints = (
        '    (("кластер", "отказоустойчив", "vrrp"), ("products/dcfw", "klasterizaciya")),\n'
        '    (("лицензи", "ugmc", "management center", "управлен"), '
        '("products/management-center", "products/dcfw", "licenzirovanie")),'
    )
    if old_hints in text and "products/management-center" not in text:
        text = text.replace(old_hints, new_hints)
        changed.append("F07: тематический проход по лицензиям")

    # F08: адреса без схемы тоже проверяем
    if "DOMAIN_ONLY_RE" not in text:
        text = text.replace(
            "ANSWER_URL_RE = re.compile",
            "DOMAIN_ONLY_RE = re.compile(\n"
            "    r\"\\b(?:[a-z0-9-]+\\.)*(?:usergate\\.com|usergate\\.ru)/[^\\s)\\]>»«\\\"',;]*\"\n"
            ")\nANSWER_URL_RE = re.compile",
            1,
        )
        old_drop = "        text = ANSWER_URL_RE.sub(bare_repl, text)"
        new_drop = '''        text = ANSWER_URL_RE.sub(bare_repl, text)

        # Адрес без схемы («docs.usergate.com/xxx») тоже не должен пережить
        # проверку, если такого пути нет среди источников.
        def domain_repl(match: re.Match) -> str:
            url = match.group(0)
            if known(url) is not None:
                return url
            dropped.append(url)
            return "на портале документации"

        text = DOMAIN_ONLY_RE.sub(domain_repl, text)'''
        if old_drop in text:
            text = text.replace(old_drop, new_drop, 1)
            changed.append("F08: проверка адресов без схемы")

    if changed:
        AGENT.write_text(text, encoding="utf-8")
        print("агент:", ", ".join(changed))


def main() -> int:
    patch_judge()
    patch_agent()
    return 0


if __name__ == "__main__":
    sys.exit(main())
