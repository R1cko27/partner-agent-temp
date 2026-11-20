---
заголовок: Настройка библиотек (Описание)
url: https://docs.usergate.com/nastrojka-bibliotek-(opisanie)_1862.html
получено: 2026-11-20 16:24 +0700
продукт: WAF
версия: 7.x
раздел: Настройка библиотек (Описание)
id_статьи: 1862
обновлено: 03 Feb, 2026
ревизия: 15
---

# Настройка библиотек (Описание)

Содержание:
Настройка IP-адресов
Группы IP-адресов создаются и настраиваются на уровне
libraries ip-list
Для создания группы IP-адресов используется команда:
Admin@nodename# create libraries ip-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название группы адресов
description
Описание группы
threat-lvl
Уровень угрозы:
very-low
— очень низкий уровень угрозы.
low
— низкий уровень угрозы.
medium
— средний уровень угрозы.
high
— высокий уровень угрозы.
very-high
— высокий уровень угрозы
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
lists
Выбор существующих групп для добавления в создаваемую группу
ips
IP-адреса или диапазон IP-адресов, которые необходимо включить в группу. Указывается в формате:
<ip>
<ip/mask>
или
<ip_range_start-ip_range_end>
Для редактирования группы (список параметров, доступных для обновления, аналогичен списку параметров команды создания группы) используется команда:
Admin@nodename# set libraries ip-list <ip-list-name> <parameter>
Чтобы добавить в список новые IP-адреса:
Admin@nodename# set libraries ip-list <ip-list-name> [ <ip1> <ip2> ... ]
Следующие команды используются для удаления всей группы IP-адресов или IP-адресов, содержащихся в ней:
Admin@nodename# delete libraries ip-list <ip-list-name>
Admin@nodename# delete libraries ip-list <ip-list-name> ips [ <ip1> <ip2>... ]
Команда отображения информации о всех имеющихся группах:
Admin@nodename# show libraries ip-list
Чтобы отобразить информацию об определенной группе, необходимо указать название интересующей группы IP-адресов:
Admin@nodename# show libraries ip-list <ip-list-name>
Также доступен просмотр содержимого группы IP-адресов:
Admin@nodename# show libraries ip-list <ip-list-name> items
Настройка user agent браузеров
Списки user agent браузеров создаются и настраивается на уровне
libraries useragents
Для добавления нового списка use ragent браузеров используется команда:
Admin@nodename# create libraries useragents <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название списка user agent
description
Описание списка
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
patterns
Шаблоны Useragent. Список Useragent браузеров доступен по ссылке:
http://www.useragentstring.com/pages/useragentstring.php
Команда для редактирования существующего списка:
Admin@nodename# set libraries useragents <useragent-list-name> <parameter>
Далее указываются параметры, которые необходимо обновить. Параметры представлены в таблице выше.
Команда для добавления новых user agent браузеров:
Admin@nodename# set libraries useragents <useragent-list-name> [ <useragent1> <useragent2> ... ]
Команды для удаления всего списка или отдельных user agent браузеров, содержащихся в нем:
Admin@nodename# delete libraries useragents <useragent-list-name>
Admin@nodename# delete libraries useragents <useragent-list-name> patterns [ <useragent> ... ]
Команда для отображения информации о всех имеющихся списках:
Admin@nodename# show libraries useragents
Чтобы отобразить информацию об определенном списке, необходимо указать название списка user agent браузеров. Команда для просмотра содержания списка user agent браузеров:
Admin@nodename# show libraries useragents <useragent-list-name> patterns
Настройка списков URL
Списки URL настраиваются на уровне
libraries url-list
Для добавления нового списка URL используется команда:
Admin@nodename# create libraries url-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название списка URL
description
Описание списка URL
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
urls
URL, которые необходимо добавить в список
case-sensitivity
Чувствительность к регистру в написании адреса URL:
sensitive
— чувствительно к регистру букв в адресе.
insensitive
— нечувствительно к регистру букв в адресе.
domain
— список адресов доменов
Команда для редактирования списка URL:
Admin@nodename# set libraries url-list <url-list-name> <parameter>
Параметры, значения которых можно обновить, представлены в таблицы выше.
Команды для удаление всего списка URL или отдельных адресов URL:
Admin@nodename# delete libraries url-list <url-list-name>
Admin@nodename# delete libraries url-list <url-list-name> urls [ <url> ... ]
Команды для просмотра информации о всех списках URL, об определённом списке URL или об адресах, входящих в определенный список:
Admin@nodename# show libraries url-list
Admin@nodename# show libraries url-list <url-list-name>
Admin@nodename# show libraries url-list <url-list-name> urls
Настройка календарей
Календари настраиваются на уровне
libraries time-sets
Для создания группы используется команда:
Admin@nodename# create libraries time-sets <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название группы
description
Описание группы
time-set
interval-name
— название интервала повторения.
type
— тип интервала повторения:
daily
— ежедневно:
time-from
— время начала (указывается в формате HH:MM).
time-to
— время окончания (указывается в формате HH:MM).
all-day on
— весь день.
weekly
— каждую неделю:
time-from
— время начала (указывается в формате HH:MM).
time-to
— время окончания (указывается в формате HH:MM).
all-day on
— весь день.
days [ Mon | Tue | Wed | Thu | Fri | Sat | Sun ]
— дни недели.
monthly
— каждый месяц:
time-from
— время начала (указывается в формате HH:MM).
time-to
— время окончания (указывается в формате HH:MM).
all-day on
— весь день.
days
— числа месяца (от 1 до 31).
fixed
— единовременно:
time-from
— время начала (указывается в формате HH:MM).
time-to
— время окончания (указывается в формате HH:MM).
all-day on
— весь день.
fixed-date
— нужная дата (указывается в формате YYYY-MM-DD).
span
— повторяющиеся события:
time-from
— время начала (указывается в формате HH:MM).
time-to
— время окончания (указывается в формате HH:MM).
all-day on
— весь день.
fixed-date-from
— дата начала (указывается в формате YYYY-MM-DD).
fixed-date-to
— дата окончания (указывается в формате YYYY-MM-DD).
range
— диапазон дат:
time-from-enabled <on/off>
— активация/деактивация параметра для указания даты начала интервала.
fixed-date-from
— дата начала (указывается в формате YYYY-MM-DD).
time-from
— время начала (указывается в формате HH:MM).
time-to-enabled <on/off>
— активация/деактивация параметра для указания даты окончания интервала.
fixed-date-to
— дата окончания (указывается в формате YYYY-MM-DD).
time-to
— время окончания (указывается в формате HH:MM)
Команда для редактирования календаря:
Admin@nodename# set libraries time-sets <time-sets-name> <parameter>
Параметры, доступные для обновления, представлены в таблице выше.
Команда для редактирования интервала, заданного в календаре:
Admin@nodename# set libraries time-sets <time-sets-name> ... time-set <time-set-type> ( <time-set-filter> )
Далее указываются новые значения;
<time-set-filter>
— фильтр по текущим значениям интервала.
Команда для добавления нового элемента в существующую группу:
Admin@nodename# create libraries time-sets <time-sets-name> ... time-set <time-set-type> new
Команда для удаления группы элементов:
Admin@nodename# delete libraries time-sets <time-sets-name>
Команда для удаления элемента календаря:
Admin@nodename# delete libraries time-sets <time-sets-name> <time-set-type> ( <time-set-filter> )
Команда для для отображения информации о всех календарях:
Admin@nodename# show libraries time-sets
Команда для отображения информации об определённом календаре:
Admin@nodename# show libraries time-sets <time-sets-name>
Команда для отображения информации об элементах группы с одинаковым типом повторения:
Admin@nodename# show libraries time-sets <time-sets-name> <time-set-type>
Настройка шаблонов страниц
Шаблоны страниц настраиваются на уровне
libraries response-pages
(доступно с версии 7.5.0).
Для добавления нового шаблона страницы используется команда:
Admin@nodename# create libraries response-pages <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название шаблона страницы
description
Описание шаблона страницы
type
Выбор типа шаблона страницы:
blockpage
— шаблон страницы блокировки.
original-template
— выбор языка шаблона:
blockpage-en
— шаблон страницы на английском.
blockpage-ru
— шаблон страницы на русском.
network-error-page
— шаблон страницы сетевых ошибок.
original-template
— выбор языка шаблона:
network-error-page-en
— шаблон страницы на английском.
network-error-page-ru
— шаблон страницы на русском
use-by-default
Назначение шаблона страницы шаблоном по умолчанию
Команда для изменения параметров шаблона страницы:
Admin@nodename# set libraries response-pages <response-page-name> <parameter>
Параметры, доступные для обновления, представлены в таблице выше.
Команда для удаления шаблона страницы:
Admin@nodename# delete libraries response-pages <response-page-name>
Примечание
Шаблон страницы, назначенный шаблоном по умолчанию, удалить нельзя.
Команда для отображения информации об определенном шаблоне страницы:
Admin@nodename# show libraries response-pages <response-page-name>
Настройка почтовых адресов
Группы почтовых адресов настраиваются на уровне
libraries email-list
Для добавления новой группы почтовых адресов используется команда:
Admin@nodename# create libraries email-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название группы почтовых адресов
description
Описание группы почтовых адресов
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
emails
Почтовые адреса, которые необходимо добавить в данную группу
Команда для редактирования информации о группе почтовых адресов:
Admin@nodename# set libraries email-list <email-list-name> <parameter>
Параметры, доступные для обновления, аналогичны параметрам, доступным при создании группы почтовых адресов.
Команды для удаления группы или почтовых адресов из нее:
Admin@nodename# delete libraries email-list <email-list-name>
Admin@nodename# delete libraries email-list <email-list-name> emails [ <email> ... ]
Команды для просмотра информации о всех созданных группах, об определенных группах или для просмотра почтовых адресов, входящих в группу:
Admin@nodename# show libraries email-list
Admin@nodename# show libraries email-list <email-list-name>
Admin@nodename# show libraries email-list <email-list-name> emails
Настройка телефонных номеров
Группы телефонных номеров настраиваются на уровне
libraries phone-list
Для создания группы телефонных номеров используется команда:
Admin@nodename# create libraries phone-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название группы телефонных номеров
description
Описание группы телефонных номеров
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
phones
Номера телефонов, которые необходимо добавить в данную группу
Команда для редактирования информации о группе телефонных номеров:
Admin@nodename# set libraries phone-list <phone-list-name> <parameter>
Параметры, доступные для обновления, представлены в таблице выше.
Команды для удаления всей группы или номеров телефонов из нее:
Admin@nodename# delete libraries phone-list <phone-list-name>
Admin@nodename# delete libraries phone-list <phone-list-name> phones [ <phone> ... ]
Команда для просмотра информации о всех созданных группах:
Admin@nodename# show libraries phone-list
Команда для просмотра информации об определенных группах телефонных номеров:
Admin@nodename# show libraries phone-list <phone-list-name>
Команда для просмотра номеров, содержащихся в группе:
Admin@nodename# show libraries phone-list <phone-list-name> phones
Настройка списка Websocket-расширений
Списки Websocket-расширений настраиваются на уровне
libraries ws-extensions-list
(доступно с версии 7.4.1).
Для создания списка расширений используется команда:
Admin@nodename# create libraries ws-extensions-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название списка Websocket-расширений
description
Описание списка
extensions
Расширения, которые необходимо включить в список
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
Команда для редактирования списка расширений:
Admin@nodename# set libraries ws-extensions-list <ws-extensions-list name> <parameter>
Параметры, значения которых можно обновить, представлены в таблицы выше.
Команды, с использованием которых доступно удаление всего списка расширений или отдельных расширений:
Admin@nodename# delete libraries ws-extensions-list <ws-extensions-list name>
Admin@nodename# delete libraries ws-extensions-list <ws-extensions-list name> extensions [ <extension> ... ]
Команды для просмотра информации о всех списках расширений, об определенном списке или о расширениях, входящих в определенный список:
Admin@nodename# show libraries ws-extensions-list
Admin@nodename# show libraries ws-extensions-list <ws-extensions-list name>
Admin@nodename# show libraries ws-extensions-list <ws-extensions-list name> extensions
Настройка списка Websocket-субпротоколов
Списки Websocket-субпротоколов настраиваются на уровне
libraries ws-protocols-list
(доступно с версии 7.4.1).
Для создания списка Websocket-субпротоколов используется команда:
Admin@nodename# create libraries ws-protocols-list <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название списка Websocket-субпротоколов
description
Описание списка
protocols
Websocket-субпротоколы, которые необходимо включить в список
type
Тип списка:
local
— локальный.
updatable
— если cписок является обновляемым, то необходимо указать адрес, с которого загружаются обновления (
url
). Периодичность обновления списка указывается параметром
shedule
в cron-формате: <минуты: 0–59> <часы: 0–23> <дни месяца: 1–31> <месяцы: 1–12> <дни недели: 0–6, где 0 — воскресенье>. При ручном вводе также можно использовать следующие символы:
Звездочка (*) — для выбора всех значений. Например, в поле для ввода часов символ означает, что резервное копирование должно выполняться каждый час.
Дефис (-) — для указания диапазона значений.
Запятая (,) — в качестве разделителя значений.
Косая черта (/) — для указания шага между значениями. Например, «2-10/2» будет означать «2,4,6,8,10», а выражение «*/2» в поле «часы» будет означать «каждые два часа»
Команда для редактирования списка Websocket-субпротоколов:
Admin@nodename# set libraries ws-protocols-list <parameter>
Параметры, значения которых можно обновить, представлены в таблицы выше.
Команды для удаления всего списка Websocket-субпротоколов или отдельных Websocket-субпротоколов:
Admin@nodename# delete libraries ws-protocols-list <ws-protocols-list name>
Admin@nodename# delete libraries ws-protocols-list <ws-protocols-list name> protocols [ <protocol> ... ]
Команды для просмотра информации о всех списках Websocket-субпротоколов, об определенном списке или о Websocket-субпротоколах, входящих в определенный список:
Admin@nodename# show libraries ws-protocols-list
Admin@nodename# show libraries ws-protocols-list <ws-protocols-list name>
Admin@nodename# show libraries ws-protocols-list <ws-protocols-list name> protocols
Настройка профилей оповещений
Профили оповещений SMTP (по эл. почте) и SMPP (по SMS) настраиваются на уровне
libraries notification-profiles
Для добавления нового профиля оповещения SMTP используется команда:
Admin@nodename# create libraries notification-profiles smtp <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название профиля
description
Описание профиля
host
IP-адрес или FQDN SMTP-сервера, который будет использоваться для отсылки почтовых сообщений
port
Порт TCP, используемый SMTP-сервером. Обычно для протокола SMTP используется порт 25, для SMTP с использованием SSL — 465. Уточните данное значение у администратора почтового сервера
connection-security
Способ безопасной отправки писем по эл. почте:
none
starttls
ssl
authentication
Включение/отключение авторизации при подключении к серверу SMTP:
off
login
Имя учетной записи для подключения к SMTP-серверу
password
Пароль учетной записи для подключения к SMTP-серверу
Для добавления нового профиля оповещения SMPP (по SMS) используется команда:
Admin@nodename# create libraries notification-profiles smpp <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название профиля
description
Описание профиля
host
IP-адрес или FQDN SMPP-сервера, который будет использоваться для отсылки SMS
port
Порт TCP, который используется для подключения к SMPP-серверу. Обычно для протокола SMPP используется порт 2775; при использовании SSL — 3550
ssl
Включение/отключение шифрования SSL:
off
login
Имя учетной записи для подключения к SMPP-серверу
password
Пароль учетной записи для подключения к SMPP-серверу
phone-translation-rules
Правила трансляции телефонных номеров. Правила используются для соответствия требованиям провайдера.
Например, если необходимо в начале всех номеров заменить «+7» на «8», используется команда
Admin@nodename# set libraries notification-profiles smpp <profile-name> phone-translation-rules + [ +7¦8 ]
source-ton
Тип номера (type of number) для источника сообщения:
0
— unknown (неизвестный).
1
— international (международный).
2
— national (государственный).
3
— network specific (сетевой специальный).
4
— subscriber number (номер абонента).
5
— alphanumeric (алфавитно-цифровой).
6
— abbreviated (сокращенный)
dest-ton
Тип номера (type of number) для адресата:
0
— unknown (неизвестный).
1
— international (международный).
2
— national (государственный).
3
— network specific (сетевой Специальный).
4
— subscriber number (номер абонента).
5
— alphanumeric (алфавитно-цифровой).
6
— abbreviated (сокращенный)
source-npi
Индикатор схемы присвоения номеров (numbering plan indicator) для источника:
0
— unknown.
1
— ISDN/telephone numbering plan (E.163/E.164).
3
— data numbering plan (X.121).
4
— telex numbering plan (F.69).
6
— land mobile (E.212).
8
— national numbering plan.
9
— private numbering plan.
10
— ERMES numbering plan (ETSI DE/PS 3 01-3).
13
— internet (IP).
18
— WAP client Id (to be defined by WAP Forum)
dest-npi
Индикатор схемы присвоения номеров (Numbering Plan Indicator) для адресата:
0
— unknown.
1
— ISDN/telephone numbering plan (E.163/E.164).
3
— data numbering plan (X.121).
4
— telex numbering plan (F.69).
6
— land mobile (E.212).
8
— national numbering plan.
9
— private numbering plan.
10
— ERMES numbering plan (ETSI DE/PS 3 01-3).
13
— internet (IP).
18
— WAP client Id (to be defined by WAP Forum)
Команда для редактирования профиля оповещения:
Admin@nodename# set libraries notification-profiles <smtp | smpp> <profile-name> <parameter>
Параметры профилей SMTP и SMPP, доступные для изменения, представлены в соответствующих таблицах выше.
Команда для удаления профиля:
Admin@nodename# delete libraries notification-profiles <smtp | smpp> <profile-name>
Также для профилей оповещений SMPP доступно удаление правил трансляции номеров:
Admin@nodename# delete libraries notification-profiles smpp <profile-name> phone-translation-rules [ phone1¦phone2 ]
Команда для отображения информации о всех имеющихся профилях оповещений:
Admin@nodename# show libraries notification-profiles
Команда для отображения информации о всех профилях одного типа:
Admin@nodename# show libraries notification-profiles <smtp | smpp>
Команда для отображения информации об определённом профиле оповещения:
Admin@nodename# show libraries notification-profiles <smtp | smpp> <profile-name>
Настройка профилей NetFlow
Профили NetFlow настраиваются на уровне
libraries netflow-profiles
Для создания профиля NetFlow используется команда:
Admin@nodename# create libraries netflow-profiles <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название профиля NetFlow
description
Описание профиля
IP-адрес NetFlow коллектора, на который сенсор будет отправлять статистику
port
UDP-порт, на котором NetFlow-коллектор будет принимать статистику
protocol
Версия протокола NetFlow, которую необходимо использовать (должна совпадать на сенсоре и коллекторе):
5
— NetFlow версии 5.
9
— NetFlow версии 9.
10
— NetFlow версии 10
active-timeout
Тайм-аут отправки статистики на коллектор до завершения потока (например, при передаче большого файла через сеть); указывается в секундах. Значение по умолчанию — 1800 секунд; максимальное значение — 3600 секунд
inactive-timeout
Тайм-аут завершения неактивного потока; указывается в секундах. Значение по умолчанию — 15 секунд; максимальное значение — 3600 секунд
max-flows
Максимальное количество учитываемых потоков, с которых собирается и отправляется статистика. По достижении указанного количества все последующие потоки не будут учитываться (ограничение необходимо для защиты от DoS-атак). Значение по умолчанию — 2 000 000; для снятия ограничения необходимо установить значение 0
nat-events
Включение/отключение отправки информации о NAT-преобразованиях в статистику NetFlow:
off
refresh-rate
Количество пакетов, после получения которого шаблон отправляется на принимающий хост (только для версий протокола NetFlow 9 и 10). Шаблон содержит информацию о настройке самого устройства и различную статистическую информацию. Значение по умолчанию — 20 пакетов
timeout-rate
Тайм-аут отправки старого шаблона на принимающий хост (только для версий протокола NetFlow 9/10). Шаблон содержит информацию о настройке самого устройства и различную статистическую информацию. Значение по умолчанию — 1800 секунд
Команда для редактирования существующего профиля NetFlow:
Admin@nodename# set libraries netflow-profiles <profile-name>
Параметры, значения которых можно изменить, представлены в таблице выше.
Команда для удаления профиля NetFlow:
Admin@nodename# delete libraries netflow-profiles <profile-name>
Команды для отображения информации о всех профилях NetFlow или об отдельном профиле:
Admin@nodename# show libraries netflow-profiles
Admin@nodename# show libraries netflow-profiles <profile-name>
Настройка LLDP-профилей
LLDP-профили (Link Layer Discovery Protocol) создаются и настраиваются на уровне
libraries lldp-profiles
Для создания LLDP-профиля используется команда:
Admin@nodename# create libraries lldp-profiles <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название LLDP-профиля
description
Описание LLDP-профиля
port-status
Режимы:
— только приём данных LLDP: UserGate не будет посылать информацию LLDP, но будет анализировать информацию LLDP от соседей
— только передача данных LLDP: UserGate будет посылать информацию LLDP, но будет отбрасывать информацию LLDP, полученную от соседей
rx-tx
— прием и передача данных LLDP: UserGate будет посылать информацию LLDP и будет анализировать информацию LLDP, полученную от соседей
Команда для редактирования информации о LLDP-профиле:
Admin@nodename# set libraries lldp-profiles <profile-name> <parameter>
Параметры, доступные для обновления, аналогичны параметрам, указываемым при создании LLDP-профиля.
Команда для удаления LLDP-профиля:
Admin@nodename# delete libraries lldp-profiles <profile-name>
Команды для отображения информации о всех LLDP-профилях или обо одном LLDP-профиле:
Admin@nodename# show libraries lldp-profiles
Admin@nodename# show libraries lldp-profiles <profile-name>
Настройка SSL-профилей
SSL-профили создаются и настраиваются на уровне
libraries ssl-profiles
Для создания SSL-профиля используется команда:
Admin@nodename# create libraries ssl-profiles <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название SSL-профиля
description
Описание SSL-профиля.
min-tls-version
Самая низкая версия TLS, которая может быть использована в данном SSL-профиле:
tls1
tls1.1
tls1.2
max-tls-version
Самая высокая версия TLS, которая может быть использована в данном SSL-профиле:
tls1
tls1.1
tls1.2
tls1.3
ssl-ciphers
Выбор необходимых алгоритмов шифрования и цифровой подписи
ssl-ciphers-suite
Установка алгоритмов шифрования для стандартных протоколов. Параметр предназначен для облегчения выбора необходимых алгоритмов шифрования и подписи для стандартных протоколов TLS; необходимо указать версию:
tls1
tls1.1
tls1.2
tls1.3
Команда для редактирования информации о SSL-профиле:
Admin@nodename# set libraries ssl-profiles <profile-name> <parameter>
Параметры, доступные для обновления, аналогичны параметрам, указываемым при создании SSL-профиля.
Команды для удаления SSL-профиля полностью или отдельных алгоритмов шифрования и цифровой подписи, заданных в нем:
Admin@nodename# delete libraries ssl-profiles <profile-name>
Admin@nodename# delete libraries ssl-profiles <profile-name> ssl-ciphers [ cipher ... ]
Команда для отображения информации о SSL-профилях:
Admin@nodename# show libraries ssl-profiles
Admin@nodename# show libraries ssl-profiles <profile-name>
Настройки библиотек
Настройки раздела журналы и отчеты

## Источник

https://docs.usergate.com/nastrojka-bibliotek-(opisanie)_1862.html
