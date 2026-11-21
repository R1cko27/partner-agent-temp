"""B5 (кеш: ключ и версия) и B4 (судья: 4-я попытка, токены и полнота в отчёте)."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = pathlib.Path("partner/api.py")
ANSWERS = pathlib.Path("partner/engine/answers.py")
JUDGE = pathlib.Path("partner/engine/judge.py")
TOOL = pathlib.Path("tools/judge_benchmark.py")


def patch_cache() -> None:
    changed = []
    text = API.read_text(encoding="utf-8")
    old = """                kb_stamp=(
                    f"{stats.get('built_at') or ''}|{data_stamp(self.settings.data_dir)}"
                ),"""
    new = """                # Только сборка индекса: правки файлов без пересборки не
                # должны обнулять кеш — индекс всё равно остаётся прежним.
                kb_stamp=f"{stats.get('built_at') or ''}","""
    if old in text:
        text = text.replace(old, new, 1)
        API.write_text(text, encoding="utf-8")
        changed.append("ключ кеша без отпечатка данных")

    text = ANSWERS.read_text(encoding="utf-8")
    if 'CACHE_VERSION = "2026-11-20.13"' in text:
        text = text.replace(
            'CACHE_VERSION = "2026-11-20.13"',
            'CACHE_VERSION = "2026-11-21.1"',
            1,
        )
        ANSWERS.write_text(text, encoding="utf-8")
        changed.append("CACHE_VERSION поднят")
    print("кеш:", ", ".join(changed) or "без изменений")


def patch_judge() -> None:
    text = JUDGE.read_text(encoding="utf-8")
    changed = []

    if "ANSWER_SYSTEM_SHORT" not in text:
        short = '''ANSWER_SYSTEM_SHORT = """Сверь ответ с эталоном. Верни ТОЛЬКО JSON:
{"verdict": "ok|partial|wrong|invented", "score": 0.0-1.0, "missing": [], "invented": [], "comment": "кратко"}"""

'''
        text = text.replace('ANSWER_SYSTEM = """', short + 'ANSWER_SYSTEM = """', 1)
        changed.append("короткий промпт")

    old_call = """        payload = (
            self._ask(system, user)
            or self._ask(system, user)
            or self._ask(system, user)
        )"""
    new_call = """        payload = self._ask(system, user)
        if not payload:
            payload = self._ask(system, user)
        if not payload:
            payload = self._ask(system, user)
        if not payload and mode != "refusal":
            # Последняя попытка — предельно короткая инструкция: иногда модель
            # тонет в правилах и не отдаёт JSON.
            payload = self._ask(ANSWER_SYSTEM_SHORT, user)"""
    if old_call in text:
        text = text.replace(old_call, new_call, 1)
        changed.append("4-я попытка")

    if changed:
        JUDGE.write_text(text, encoding="utf-8")
    print("судья:", ", ".join(changed) or "без изменений")


def patch_tool() -> None:
    text = TOOL.read_text(encoding="utf-8")
    changed = []

    if "_anchor_completeness" not in text:
        helper = '''ANCHOR_RE = re.compile(r"\\b\\d+[.,]?\\d*\\b|\\b[A-ZА-Я]{2,}\\b|\\b[A-Za-z]+[0-9][A-Za-z0-9.]*\\b")


def _anchor_completeness(reference: str, answer: str) -> Optional[float]:
    """Полнота без must_contain: доля чисел, кодов и аббревиатур эталона."""
    anchors = [item for item in ANCHOR_RE.findall(reference or "") if len(item) >= 2]
    anchors = list(dict.fromkeys(anchors))[:12]
    if not anchors:
        return None
    body = (answer or "").lower()
    return round(sum(1 for item in anchors if item.lower() in body) / len(anchors), 2)


'''
        text = text.replace("def load_cases(", helper + "def load_cases(", 1)
        changed.append("якорная полнота")

    old = """        completeness = round(len(covered) / len(must), 2) if must else None"""
    new = """        completeness = round(len(covered) / len(must), 2) if must else None
        if completeness is None:
            completeness = _anchor_completeness(case.get("reference") or "", answer)"""
    if old in text and "if completeness is None:" not in text:
        text = text.replace(old, new, 1)
        changed.append("полнота без must")

    old_row = '            "completeness": completeness,'
    new_row = '            "completeness": completeness,\n            "tokens": int((done.get("usage_total") or {}).get("total_tokens") or 0),'
    if old_row in text and '"tokens":' not in text:
        text = text.replace(old_row, new_row, 1)
        changed.append("токены в отчёте")

    if changed:
        TOOL.write_text(text, encoding="utf-8")
    print("прогон:", ", ".join(changed) or "без изменений")


def main() -> int:
    patch_cache()
    patch_judge()
    patch_tool()
    return 0


if __name__ == "__main__":
    sys.exit(main())
