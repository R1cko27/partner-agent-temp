# Partner-Agent — ИИ-консультант по продуктам UserGate

RAG-ассистент по базе знаний компании UserGate: отвечает по документации, карточкам продуктов
и FAQ, показывает источники и предлагает продолжения. Два интерфейса:

- **index** (`/`) — рабочий чат сотрудника: рассуждения, инструменты, история, все источники;
- **site** (`/site.html`) — клиентская панель: короткие ответы, опросы, кнопки-продолжения.

![Пустое состояние](docs/ui-empty.png)
![Ответ с источниками](docs/ui-chat.png)

## Быстрый старт

```powershell
cd D:\hacaton\test_rag_system\partner-agent

# виртуальное окружение лежит рядом с проектом
..\.venv\Scripts\python.exe app.py            # http://127.0.0.1:8001
```

Полезные режимы запуска:

```powershell
..\.venv\Scripts\python.exe app.py --port 8010 --no-browser
..\.venv\Scripts\python.exe app.py --ingest   # пересобрать индекс перед запуском
```

Настройки — в `.env` (образец: `.env.example`). Минимально нужен `DEEPSEEK_API_KEY`;
доступ к API защищён `API_TOKEN` (заголовок `X-Api-Token`).

## Структура проекта

```
partner-agent/
├── app.py                  запуск FastAPI (uvicorn) + браузер
├── ingest.py               сборка базы знаний: BM25 + эмбеддинги + Chroma
├── run.bat                 запуск через venv
├── partner/
│   ├── api.py              HTTP-слой: чат, сессии, статика, студия
│   ├── agent.py            оркестратор ответа: режимы, контекст, инструменты, постобработка
│   ├── prompts.py          сборка системных промптов и правил стиля
│   ├── schemas.py          Pydantic-модели запросов/ответов
│   ├── followups.py        планировщик кнопок-продолжений по базе
│   ├── config.py           настройки, пути, лимиты
│   ├── domain/             ретривер, сущности, источники, дельта-слой
│   ├── engine/             LLM-клиент, BM25, эмбеддинги, Chroma, судья, БД, чанкинг
│   └── web/                статические страницы: index, site, docs, studio
├── data/company/           база знаний: профиль, правила, about/products/faq/news/docs
├── storage/                рабочие данные (индекс, Chroma, модели, SQLite)
├── tests/                  тесты и эталонные вопросы
├── tools/                  скрипты сборки, аудита и оценки качества
├── deploy/                 сборка для хостинга (host/, zip, start.ps1)
└── docs/                   скриншоты и описание UI
```

## База знаний

```
data/company/
├── profile.json        карточка компании: контакты, продукты, факты
├── agent.json          профиль ассистента: роль, правила, глоссарий, брендинг
├── urls.txt            страницы, которые скачиваются при полной сборке
├── about/ products/ faq/ news/ team/     курируемые материалы
└── docs/               документы + crawl/ (страницы docs.usergate.com и habr)
```

Объём: ~3 460 файлов материалов, **36 615 фрагментов** в индексе
(сборка от 2026-11-22 11:45).

Все факты имеют источник; правила «не обобщать, не переносить между продуктами,
не выдумывать цены» зашиты в `agent.json` (43 правила).

## Как формируется ответ

1. **Выбор режима.** Для фактовых вопросов — локальная эвристика (fast), для расплывчатых
   («помоги подобрать», «хочу…») — короткий вызов модели и режим `clarify` с опросом.
2. **Поиск.** Гибрид: BM25 + вектор + сущности, слияние через RRF (K=60), затем отбор
   по типам источников, дедупликация и лимит на документ.
3. **Контекст.** До 4 фрагментов по 650 символов, бюджет 5 000 символов; официальные
   факты (контакты, оглавления) поднимаются прицельно по интенту.
4. **Генерация.** Один вызов DeepSeek (`deepseek-flash`), лимит 4 000 токенов.
5. **Постобработка.** Таблицы, сноски `[1]`, ссылки, чистка обрывов.
6. **Кнопки.** 2–3 продолжения: одно из заголовка ответа, остальные — коротким вызовом модели.

Типичное время ответа: **6–9 секунд** (ответ ~3,5 с + кнопки ~2 с).

### Параметры поиска (`data/company/agent.json`)

```json
"top_k": 8, "context_hits": 4, "excerpt_chars": 650,
"context_budget_chars": 5000, "max_per_doc": 3,
"kind_weights": {"doc": 1.35, "faq": 1.2, "product": 1.1, "about": 1.1, "company": 0.9, "news": 0.55}
```

### Режимы

| Режим | Когда | Особенность |
|---|---|---|
| `fast` / `auto` | простые факты | один вызов модели, без инструментов |
| `thinking` | сравнения, разбор | инструменты, до 2 шагов |
| `clarify` | расплывчатый запрос | опрос на 4–8 вопросов |
| `direct` | ответы после опроса | без повторного поиска |

## Интерфейсы

**index** — чат сотрудника: markdown с таблицами, сноски `[1]` кликабельны, кнопки-продолжения,
панель «Размышление/Действия», сессии, тёмная тема.

**site** — клиентская панель: стартовые вопросы, печать ответа с markdown, блок «Источники»,
опросы, 2–3 кнопки. После третьего вопроса предлагается перейти в полный чат.

Общие правила: сообщения оформляются до появления кнопок; под опросом кнопок нет;
приветствия не предлагают уточнений; адреса и номера берутся дословно из источников.

## API

| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/chat` | поток SSE: `session`, `delta`, `sources`, `clarification`, `done`, `followups` |
| GET | `/api/health` | статус, статистика базы |
| GET | `/api/agent/profile` | профиль и брендинг |
| POST | `/api/retrieve` | поиск фрагментов без генерации |
| GET/POST | `/api/sessions` | список/создание сессий (`?mine=1` — только свои) |
| GET/PATCH/DELETE | `/api/sessions/{id}` | история, переименование, удаление |
| DELETE | `/api/cache` | очистка кэша ответов |
| GET | `/api/session/current` | сессия текущего клиента по куке |
| GET | `/site.html`, `/docs.html`, `/studio` | страницы |

Авторизация: `X-Api-Token`. Сессии: куки `ug_session`/`ug_client` только для index;
сайт передаёт свой `session_id` и не перетирает сессию сотрудника.

## Сборка и обновление базы

```powershell
# полная сборка (BM25 + эмбеддинги + Chroma), ~45 минут
..\.venv\Scripts\python.exe ingest.py

# без скачивания внешних страниц
..\.venv\Scripts\python.exe ingest.py --no-web

# сборка в отдельные каталоги, не трогая рабочую базу
..\.venv\Scripts\python.exe ingest.py `
  --index-subdir index-v2 --chroma-subdir chroma-v2 --collection s2ze_kb_v2

# добавить один документ в поиск без пересборки (delta-слой)
..\.venv\Scripts\python.exe tools\add_docs.py --file data/company/docs/doc.md --as docs/doc.md
```

Сборка парсит `data/company/**` через конвертеры (PDF, DOCX, HTML, MD, TXT, JSON, CSV).

## Тесты и оценка качества

```powershell
..\.venv\Scripts\python.exe tests\test_partner.py            # 25 тестов
..\.venv\Scripts\python.exe tools\ctx_eval.py E02 R07 R16   # контекст на выбранных вопросах
..\.venv\Scripts\python.exe tools\run60.py tests\benchmark-60-usergate-2026-11-22.json --limit 30
```

Последний прогон 30 вопросов: **средняя 0,51** (формат 0,84 · кнопки 0,64 ·
полнота 0,56 · источники 0,51 · контекст 0,34). Отчёт: `tools/_run60_report.json`.

## Инструменты (`tools/`)

| Категория | Скрипты |
|---|---|
| Сборка данных | `crawl_site.py`, `add_docs.py`, `build_source_links.py`, `build_docs_page.py` |
| Интерфейс | `build_site_page4.py`, `build_host_bundle.py` |
| Оценка | `run60.py`, `ctx_eval.py`, `quality_gate.py`, `judge_benchmark.py`, `rescore_benchmark.py` |
| Аудит базы | `data_audit.py`, `fact_audit.py`, `entity_check.py`, `find_conflicts.py`, `check_sources.py` |
| Экспорт | `export_telegram.py`, `export_vk.py`, `export_habr.py` |

## Деплой

```powershell
..\.venv\Scripts\python.exe tools\build_host_bundle.py   # deploy/host/
Compress-Archive -Path deploy\host\* -DestinationPath deploy\partner-agent-site.zip -Force
```

`deploy/host/` — статика для хостинга, `deploy/start.ps1` — запуск на сервере.
Публичный доступ — через cloudflared quick tunnel:

```powershell
tools\cloudflared.exe tunnel --url http://127.0.0.1:8001 --no-autoupdate
```

Поддомен меняется при каждом запуске; для постоянного адреса нужен именованный туннель.

## Конфигурация

`.env`:

```ini
LLM_PROVIDER=deepseek
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_API_KEY=...
API_TOKEN=...
LLM_TEMPERATURE=0
```

Лимиты и параметры поиска — `data/company/agent.json` (`limits`, `retrieval`, `rules`).

## Ограничения

- `usergate.com/products`, `/academy/courses-exams`, `/registry-entry` — SPA, автоматически
  не скачиваются; это канонические адреса для проверки человеком.
- Часть разделов документации (журналы DCFW 8.x) ещё не обойдена.
- Вебинары 2026 добавлены вручную (`data/company/news/2026-webinars.md`); при полной
  пересборке подхватываются автоматически.
- Контекст остаётся слабым местом (0,34): в top-4 иногда попадают обзорные страницы.

## Бэкапы

```
D:\hacaton\backups\partner-agent-MAIN-20261122-1429   полный бэкап проекта
D:\hacaton\backups\storage-legacy-20261122           старые индексы и Chroma
```
