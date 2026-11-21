---
заголовок: Общие настройки консоли управляемой области
url: https://docs.usergate.com/obshie-nastrojki-konsoli-upravlyaemoj-oblasti_1420.html
источник: портал документации
получено: 2026-11-20 16:33 +0700
продукт: Management Center
версия: 7.x
раздел: Режим администратора управляемой области
id_статьи: 1420
обновлено: 21 Mar, 2024
ревизия: 5
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Режим администратора управляемой области / Общие настройки консоли управляемой области
---

# Общие настройки консоли управляемой области

Documentation:
Общие настройки консоли управляемой области задаются на уровне
settings general
. Структура команды для настройки одного из разделов (<settings-module>):
realmadmin/realm@nodename# set settings general <settings-module>
Доступна настройка следующих разделов:
Параметр
Описание
admin-console
Настройки интерфейса (уровень
settings general admin-console
timezone
: часовой пояс, соответствующий вашему местоположению. Часовой пояс используется в расписаниях, применяемых в правилах, а также для корректного отображения времени и даты в отчетах, журналах и т.п
api-session-lifetime
: время ожидания сеанса администратора в секундах.
change-tracker
Настройка учета изменений (уровень settings general change-tracker):
enabled
: включение/отключение учёта изменений.
off
event-tracker-types
: типы изменений задаются администратором. Для удаления типа изменения используется команда:
realmadmin/realm@nodename# delete settings general change-tracker event-tracker-types [ type1 ... ]
v7.x
Режим конфигурации администратора управляемой области
Администраторы управляемой области

## Источник

https://docs.usergate.com/obshie-nastrojki-konsoli-upravlyaemoj-oblasti_1420.html
