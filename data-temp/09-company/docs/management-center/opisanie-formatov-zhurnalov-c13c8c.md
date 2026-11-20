---
заголовок: Описание форматов журналов
url: https://docs.usergate.com/opisanie-formatov-zhurnalov_1312.html
получено: 2026-11-20 16:30 +0700
продукт: Management Center
версия: 7.x
раздел: Журналы и отчёты
id_статьи: 1312
обновлено: 31 Mar, 2026
ревизия: 1
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Журналы и отчёты / Описание форматов журналов
---

# Описание форматов журналов

Содержание:
Documentation:
Формат журнала событий
CEF
Тип поля
Название поля
Описание
Пример значения
CEF заголовок
CEF:Version
Версия CEF.
CEF:0
Device Vendor
Производитель продукта.
UserGate
Device Product
Тип продукта.
NGFW
Device Version
Версия продукта.
7
Source
Тип журнала.
events
Origin
Модуль, в котором произошло событие.
admin_console
Severity
Важность события.
Может принимать значения:
0 — информационные.
6 — предупреждения.
8 — ошибки.
10 — критичные.
CEF [расширение]
Время, когда было получено событие: миллисекунды с 1 января 1970 года.
1652344423822
deviceExternalId
Имя, которое однозначно идентифицирует устройство, генерирующее это событие.
mc_core@einersonstal
suser
Имя пользователя.
Administrator (Admin)
cat
Компонент, в котором произошло событие.
console_auth
act
Тип события.
administrator_login
src
IPv4-адрес источника.
192.168.117.254
cs1Label
Поле используется для указания деталей события.
Attributes
cs1
Детали события в формате JSON.
{"login":"ex_admin","realm_id":"31d8fcb6-e51d-4e3f-b799-181d31a45b06"}
JSON
Название поля
Описание
Пример значения
user
Имя пользователя.
Admin
timestamp
Время получения события в формате: yyyy-mm-ddThh:mm:ssZ.
2022-05-12T08:11:46.15869Z
ip_address
IPv4-адрес источника события.
192.168.174.134
node
Имя, которое однозначно идентифицирует устройство, генерирующее это событие.
mc_core@einersonstal
attributes
Детали события в формате JSON.
{"rule":{"logrotate":12,"attributes":{"timezone":"Asia/Novosibirsk"},"id":"66f9de9f-d698-4bec-b3b0-ba65b46d3608","name":"Example log export ftp"}
event_type
Тип события.
logexport_rule_updated
event_severity
Важность события.
info (информационные), warning (предупреждения), error (ошибки), critical (критичные).
event_origin
Модуль, в котором произошло событие.
core
event_component
Компонент, в котором произошло событие.
console_auth
Режим расширенного поиска
Диагностика и мониторинг

## Источник

https://docs.usergate.com/opisanie-formatov-zhurnalov_1312.html
