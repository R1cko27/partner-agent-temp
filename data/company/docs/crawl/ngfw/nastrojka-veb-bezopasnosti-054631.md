---
заголовок: Настройка веб-безопасности
url: https://docs.usergate.com/nastrojka-veb-bezopasnosti_823.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка веб-безопасности
id_статьи: 823
обновлено: 19 Feb, 2026
ревизия: 11
---

# Настройка веб-безопасности

Documentation:
Настройка веб-безопасности производится на уровне
security-policy safe-browsing
. Подробнее о структуре команд читайте в разделе
UserGate Policy Language
Для создания правила веб-безопасности используется команда:
Admin@nodename# create security-policy safe-browsing <position> upl-rule
Параметры правил веб-безопасности:
Параметр
Описание
Действие для создания правила с помощью UPL.
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила веб-безопасности.
Например:
name("Safe browsing rule example")
desc
Описание правила, например,
desc("Safe browsing rule example set via CLI")
rule_log
Запись в журнал информации о трафике при срабатывании правила. Возможны варианты:
rule_log(no)
или
rule_log(false)
- отключить журналирование. Если при создании правила
rule_log
не указано, функция журналирования отключена.
rule_log(yes)
или
rule_log(true)
- включить журналирование
enable_adblock
Блокировка рекламы
enable_adblock(yes)
или
enable_adblock(true)
enable_adblock(no)
или
enable_adblock(false)
url_list_exclusions
Список сайтов, для которых блокировать рекламу не требуется:
url_list_exclusions("URL list name")
О создании и настройке списков URL с использованием CLI читайте в разделе
Настройка списков URL
enable_injector
Инжектирование кода в веб страницы:
enable_injector(yes)
или
enable_injector(true)
enable_injector(no)
или
enable_injector(false)
custom_injector
Код инжектора.
safe_search
Использование функции безопасного поиска:
safe_search(yes)
или
safe_search(true)
safe_search(no)
или
safe_search(false)
search_history_logging
Журналирование поисковых запросов пользователей:
search_history_logging(no)
или
search_history_logging(false)
- отключить журналирование поисковых запросов пользователей. Если при создании правила
search_history_logging
не указано, функция журналирования отключена.
search_history_logging(yes)
или
search_history_logging(true)
- включить журналирование поисковых запросов пользователей.
social_sites_block
Блокировка приложений социальных сетей:
social_sites_block(yes)
или
social_sites_block(true)
social_sites_block(no)
или
social_sites_block(false)
src.zone
Зона источника трафика.
Для указания зоны источника, например, Trusted:
src.zone = Trusted
Подробнее о настройке зон с использованием интерфейса командной строки читайте в разделе
Зоны
src.ip
Добавление списков IP-адресов или доменов источника.
Для указания списка IP-адресов:
src.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI читайте в разделе
Настройка IP-адресов
Для указания списка доменов источника:
src.ip = lib.url()
; в скобках необходимо указать название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки читайте в разделе
Настройка списков URL
src.geoip
Указание GeoIP источника; необходимо указать код страны (например,
src.geoip
= RU
Коды названий стран доступны по ссылке
ISO 3166-1
user
Пользователи и группы пользователей, для которых применяется правило веб-безопасности (локальные или LDAP).
Для добавления LDAP групп и пользователей необходим корректно настроенный LDAP-коннектор (о настройке LDAP-коннектора через CLI читайте в разделе
Настройка LDAP-коннектора
Примеры добавления пользователей в правило:
user = known
user = "user"
user = "testd.local\\user1"
user = ("user", "testd.local\\user1")
time
Настройка расписания работы правила.
Для установки расписания:
time = lib.time()
; в скобках необходимо указать название группы календарей. Подробнее о настройке календарей читайте в разделе
Настройка календарей
Для редактирования правил веб-безопасности используется команда:
Admin@nodename# set security-policy safe-browsing <position> upl-rule
Для просмотра всех созданных правил веб-безопасности используется команда:
Admin@nodename# show security-policy safe-browsing
Для просмотра определенного правила веб-безопасности используется команда:
Admin@nodename# show security-policy safe-browsing <position>
Пример создания правила веб-безопасности с помощью UPL:
Admin@nodename# create security-policy safe-browsing 1 upl-rule PASS \
...user = known \
...src.zone = Trusted \
...enable_adblock(yes) \
...safe_search(yes) \
...rule_log(yes) \
...name("Test safe browsing rule") \
...desc("Test safe browsing rule description") \
...enabled(true)
...
Admin@nodename# show security-policy safe-browsing 1
% ----------------- 1 -----------------
OK \
user = known \
src.zone = Trusted \
rule_log(yes) \
enable_adblock(yes) \
safe_search(yes) \
desc("Test safe browsing rule description") \
enabled(true) \
id("406a2753-750e-4830-82a8-583043e72359") \
name("Test safe browsing rule")
Для удаления правила веб-безопасности используется команда:
Admin@nodename# delete security-policy safe-browsing <position>
v7.x
Настройка фильтрации контента
Настройка правил инспектирования туннелей

## Источник

https://docs.usergate.com/nastrojka-veb-bezopasnosti_823.html
