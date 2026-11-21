"""Streamlit-интерфейс RAG-прототипа.

Запуск:
    streamlit run app.py

Данные складываются в ./storage (ChromaDB + манифест) и ./data (локальные документы).
Загрузка новых документов и ссылок только добавляет записи в существующую базу.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from core import Embedder, Store, chunk_text, load_folder, load_url
from llm import NO_DATA, LLMError, answer, provider_defaults

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
DATA_DIR = BASE_DIR / "data"

try:  # необязательная зависимость: удобно держать ключ в .env
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except Exception:  # noqa: BLE001
    pass

st.set_page_config(page_title="RAG-прототип", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_pipeline(storage_path: str):
    """Эмбеддер и хранилище создаются один раз за сессию."""
    embedder = Embedder(cache_dir=Path(storage_path) / "models")
    store = Store(Path(storage_path), embedder)
    return embedder, store


embedder, store = get_pipeline(str(STORAGE_DIR))

st.title("RAG-прототип: документы, ссылки и поиск")
st.caption(
    "PDF и TXT из локальной папки + страницы по ссылке → чанки 800/150 → эмбеддинги → ChromaDB. "
    "Новые материалы добавляются в существующую базу, старая не стирается."
)

if not embedder.available:
    st.error(
        "Модель эмбеддингов недоступна, индексация и поиск работать не будут. "
        f"Подробность: {embedder.error or 'нет модели'}"
    )

# --- боковая панель -----------------------------------------------------
with st.sidebar:
    st.header("Модель")
    provider = st.radio(
        "Провайдер",
        options=["openrouter", "local"],
        format_func=lambda value: "OpenRouter" if value == "openrouter" else "Локальная (Ollama)",
        help="OpenRouter — облако по API-ключу. Локальная — OpenAI-совместимый сервер, например Ollama.",
    )
    default_url, default_model = provider_defaults(provider)
    model = st.text_input("Модель", value=default_model)
    base_url = st.text_input("Base URL", value=default_url)
    if provider == "openrouter":
        api_key = st.text_input(
            "OPENROUTER_API_KEY",
            value=os.environ.get("OPENROUTER_API_KEY", ""),
            type="password",
            help="Ключ можно положить в .env — поле подставится автоматически.",
        )
    else:
        api_key = st.text_input(
            "Ключ (для Ollama не нужен)",
            value=os.environ.get("LOCAL_API_KEY", "ollama"),
            type="password",
        )

    st.divider()
    st.header("Поиск")
    top_k = st.slider("Сколько фрагментов брать", 1, 10, 3)
    temperature = st.slider("Температура", 0.0, 1.0, 0.1, 0.1)
    show_chunks = st.toggle("Показывать найденные фрагменты", value=True)

    st.divider()
    st.metric("Фрагментов в базе", store.count())
    st.metric("Документов", len(store.documents()))

    if provider == "local":
        st.caption(f"Проверьте, что сервер отвечает на {base_url}")

search_tab, index_tab, base_tab = st.tabs(["Поиск", "Индексирование", "База"])

# --- поиск --------------------------------------------------------------
with search_tab:
    question = st.text_input(
        "Вопрос по загруженным документам",
        placeholder="Например: какие требования к кластеру?",
    )
    submitted = st.button("Найти ответ", type="primary", disabled=not question.strip())

    if submitted:
        with st.spinner("Ищу релевантные фрагменты…"):
            hits = store.search(question, k=top_k)

        if not hits:
            st.warning(NO_DATA)
            st.caption(
                "Либо в базе нет близких фрагментов, либо она пуста — загрузите документы "
                "на вкладке «Индексирование»."
            )
        else:
            try:
                with st.spinner("Модель формулирует ответ…"):
                    result = answer(
                        question,
                        hits,
                        provider=provider,
                        model=model,
                        api_key=api_key,
                        base_url=base_url,
                        temperature=temperature,
                    )
                st.subheader("Ответ")
                st.markdown(result["text"])
                if NO_DATA in result["text"]:
                    st.info(
                        "Модель не нашла ответа в контексте. Это штатное поведение: "
                        "выдумывать она не должна."
                    )
            except LLMError as exc:
                st.error(f"Модель недоступна: {exc}")
                st.info(
                    "Ниже — найденные фрагменты. Их достаточно, чтобы ответить вручную "
                    "или проверить, что база вообще содержит нужное."
                )

            sources = []
            for hit in hits:
                source = hit.get("source") or hit.get("title")
                if source and source not in sources:
                    sources.append(source)
            if sources:
                st.subheader("Источники")
                for source in sources:
                    st.markdown(f"- {source}")

            if show_chunks:
                with st.expander(f"Найденные фрагменты ({len(hits)})", expanded=False):
                    for position, hit in enumerate(hits, start=1):
                        st.markdown(
                            f"**{position}. {hit.get('title') or 'без названия'}** "
                            f"· схожесть `{hit.get('score')}` · {hit.get('source')}"
                        )
                        st.text(hit.get("text", "")[:1200])
                        st.divider()

# --- индексирование -----------------------------------------------------
with index_tab:
    st.subheader("Локальная папка")
    st.caption("Читаются все PDF и TXT, включая вложенные папки. Повторная индексация не создаёт дублей.")
    folder = st.text_input("Путь к папке", value=str(DATA_DIR))
    if st.button("Проиндексировать папку"):
        path = Path(folder).expanduser()
        with st.spinner("Читаю документы…"):
            documents, errors = load_folder(path)
        if not documents:
            st.warning("В папке не нашлось PDF или TXT.")
            for error in errors:
                st.caption(f"! {error}")
        else:
            progress = st.progress(0.0, text="Индексирую…")

            def report_progress(message: str) -> None:
                progress.text = message

            with st.spinner("Считаю эмбеддинги и пишу в ChromaDB…"):
                report = store.add_documents(documents, progress=report_progress)
            progress.empty()
            st.success(
                f"Добавлено документов: {report['added_docs']}, "
                f"фрагментов: {report['chunks']}, пропущено как уже загруженные: {report['skipped']}"
            )
            for error in report["errors"] + errors:
                st.caption(f"! {error}")

    st.divider()
    st.subheader("Ссылка")
    st.caption("Страница скачивается, из неё вырезаются script/style/nav/footer, текст сохраняется с URL как источником.")
    url = st.text_input("URL", placeholder="https://example.com/page")
    if st.button("Добавить ссылку", disabled=not url.strip()):
        with st.spinner("Скачиваю страницу…"):
            try:
                document = load_url(url.strip())
            except Exception as exc:  # noqa: BLE001
                st.error(f"Не удалось загрузить страницу: {exc}")
                document = None
        if document is not None:
            if not document.text.strip():
                st.warning("Со страницы не удалось извлечь текст — возможно, контент грузится скриптами.")
            else:
                with st.spinner("Считаю эмбеддинги…"):
                    report = store.add_documents([document])
                if report["added_docs"]:
                    st.success(f"Добавлено фрагментов: {report['chunks']} · источник: {document.source}")
                elif report["skipped"]:
                    st.info("Эта страница уже в базе, повторно не добавляю.")
                for error in report["errors"]:
                    st.caption(f"! {error}")

    st.divider()
    st.subheader("Предпросмотр чанкинга")
    sample = st.text_area("Вставьте текст, чтобы увидеть, как он нарежется", height=140)
    if sample:
        pieces = chunk_text(sample)
        st.caption(f"Получилось фрагментов: {len(pieces)}")
        for index, piece in enumerate(pieces, start=1):
            with st.expander(f"Фрагмент {index} · {len(piece)} символов"):
                st.text(piece)

# --- база ---------------------------------------------------------------
with base_tab:
    st.subheader("Что уже загружено")
    st.write(f"Фрагментов в коллекции: **{store.count()}**")
    documents = store.documents()
    if not documents:
        st.info("База пуста. Загрузите документы на вкладке «Индексирование».")
    else:
        st.dataframe(documents, use_container_width=True, hide_index=True)

        st.divider()
        with st.expander("Удалить документ из базы"):
            st.caption(
                "Удаление — единственное действие, которое убирает данные. "
                "Обычная индексация только добавляет материалы."
            )
            labels = {f"{item['source']} · {item['chunks']} фрагм.": item["doc_id"] for item in documents}
            choice = st.selectbox("Документ", options=list(labels))
            confirm = st.checkbox("Подтверждаю удаление")
            if st.button("Удалить", disabled=not confirm):
                removed = store.drop_document(labels[choice])
                st.success(f"Удалено фрагментов: {removed}")
                st.rerun()

            st.divider()
            if st.button("Удалить всю базу", disabled=True):
                st.caption(
                    "Намеренно отключено: прототип не должен перезаписывать базу. "
                    "Если нужно полностью начать заново — удалите папку storage вручную."
                )
