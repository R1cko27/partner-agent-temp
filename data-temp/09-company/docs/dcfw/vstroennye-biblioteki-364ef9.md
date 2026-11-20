---
заголовок: Встроенные библиотеки
url: https://docs.usergate.com/vstroennye-biblioteki_1742.html
получено: 2026-11-20 16:25 +0700
продукт: DCFW
версия: 8.x
раздел: Встроенные библиотеки
id_статьи: 1742
обновлено: 19 Nov, 2024
ревизия: 3
---

# Встроенные библиотеки

Библиотеки (
lib
) — это элементы языка UPL, которые служат для доступа к встроенным и пользовательским библиотекам. Как правило, это достаточно большие списки, которые неудобно описывать через определения
def
. Обращение к библиотекам происходит по их именам.
Синтаксис
library ::= lib.<url | morphology | category | useragent | mime | network | time | applicationgroup | servicegroup>(list_names)
list_names ::= name list_names
name ::= word | string
url
— список URL;
morphology
— список морфологических словарей;
category
— группа категорий;
useragent
— список юзерагентов;
mime
— список типов контента;
network
— список сетей/IP-адресов;
time
— библиотека с промежутками времени.
Пример
DENY src.ip = lib.network("Bad ips", "Test ips")
DENY dst.ip = lib.network("Bad ips")
DENY dst.ip = lib.url("Bad urls") % в данном случае домены будут резолвиться в ip-адреса
DENY morphology = lib.morphology("Porno words", "Bad words")
DENY category = lib.category("Restricted categories") category = lib.category(Productivity)
PASS request.header.User-Agent = lib.useragent("Browsers")
PASS request.header.Content-Type = lib.mime(Applications)
DENY time = lib.time(Weekends)
v8.x
Условия
Определения

## Источник

https://docs.usergate.com/vstroennye-biblioteki_1742.html
