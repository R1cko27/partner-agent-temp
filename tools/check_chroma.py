r"""Проверка, работает ли Chroma в вашем окружении.

Запускать в обычном окне (не в песочнице агента):

    py tools\check_chroma.py

Скрипт создаёт временную базу, пишет одну запись и удаляет её.
"""

from __future__ import annotations

import io
import pathlib
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGET = pathlib.Path("storage") / "_chroma_check"


def main() -> int:
    try:
        import chromadb
    except Exception as exc:  # noqa: BLE001
        print("chromadb не импортируется:", type(exc).__name__, exc)
        return 1

    print("chromadb:", chromadb.__version__)
    shutil.rmtree(TARGET, ignore_errors=True)
    TARGET.mkdir(parents=True, exist_ok=True)
    try:
        client = chromadb.PersistentClient(path=str(TARGET.resolve()))
        collection = client.get_or_create_collection("check")
        collection.add(
            ids=["probe"],
            embeddings=[[0.1] * 8],
            documents=["проверка"],
            metadatas=[{"k": "v"}],
        )
        print("Chroma работает: записей", collection.count())
        ok = True
    except Exception as exc:  # noqa: BLE001
        print("Chroma НЕ работает:", type(exc).__name__, str(exc)[:200])
        ok = False
    finally:
        shutil.rmtree(TARGET, ignore_errors=True)

    if ok:
        print("\nМожно пересобирать в Chroma:")
        print("  1) остановите app.py")
        print("  2) удалите storage\\chroma, storage\\chroma-v2")
        print("  3) в .env: CHROMA_SUBDIR=chroma")
        print("  4) py ingest.py")
    else:
        print("\nChroma недоступна и здесь — оставляем vectors.npz, всё работает на нём.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
