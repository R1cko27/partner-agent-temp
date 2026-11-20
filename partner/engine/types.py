"""Типы, общие для движка и предметной области."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    """Единица знания: карточка компании, продукт, человек, FAQ или сырой файл."""

    doc_id: str
    text: str
    kind: str
    title: str
    source: str
    entities: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    no_split: bool = False
