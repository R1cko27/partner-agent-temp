---
заголовок: Встроенные библиотеки
url: https://docs.usergate.com/vstroennye-biblioteki_1867.html
получено: 2026-11-20 16:21 +0700
продукт: WAF
версия: 7.x
раздел: Встроенные библиотеки
id_статьи: 1867
обновлено: 24 Jan, 2025
ревизия: 3
---

# Встроенные библиотеки

Библиотеки (
lib
) — это элементы языка UPL, которые служат для доступа к встроенным и пользовательским библиотекам. Как правило, это достаточно большие списки, которые неудобно описывать через определения def. Обращение к библиотекам происходит по их именам.
Синтаксис
library ::= lib.<url | useragent | network | time>(list_names)
list_names ::= name list_names
name ::= word | string
url
— список URL;
useragent
— список юзерагентов;
network
— список сетей/IP-адресов;
time
— библиотека с промежутками времени.
Пример
DENY src.ip = lib.network("Bad ips", "Test ips")
DENY dst.ip = lib.network("Bad ips")
DENY dst.ip = lib.url("Bad urls") % в данном случае домены будут резолвиться в ip-адреса
PASS request.header.User-Agent = lib.useragent("Browsers")
DENY time = lib.time(Weekends)
v7.x
Условия
Определения

## Источник

https://docs.usergate.com/vstroennye-biblioteki_1867.html
