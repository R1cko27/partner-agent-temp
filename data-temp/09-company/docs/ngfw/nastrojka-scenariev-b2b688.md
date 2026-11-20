---
заголовок: Настройка сценариев
url: https://docs.usergate.com/nastrojka-scenariev_687.html
источник: портал документации
получено: 2026-11-20 16:18 +0700
продукт: NGFW
версия: 7.0.1
раздел: Настройка сценариев
id_статьи: 687
обновлено: 22 Jan, 2024
ревизия: 4
---

# Настройка сценариев

Содержание:
Documentation:
Настройка сценариев происходит на уровне
security-policy scenarios
с использованием UPL (подробнее об UserGate Policy Language читайте в разделе
Настройка правил с использованием UPL
Для задания условий сценариев и их объединения используются определения (definitions). Каждому определению присваивается уникальное пользовательское имя, по которому к нему можно будет обратиться. Условия сценария могут быть написаны в одной строке или разбиты с помощью обратного слэша (как при использовании многострочного ввода).
Для создания/изменения условий сценариев используется функция
def scenario_cond
, которая в общем виде имеет следующую структуру:
def scenario_cond <scenario_condition_name>
scenario_conditions
end
Параметры, использующиеся для задания разных типов условий, будут рассмотрены в следующих разделах.
Далее, после указания условий, указываются общие свойства сценария, представленные в таблице ниже:
Наименование
Описание
Действие для создания сценария.
scenario_cond
Пользовательское имя определения, содержащего список условий сценария:
scenario_cond = condition_example
enabled
Включить/отключить использование сценария:
enabled(true)
enabled(false)
name
Задать имя сценария:
name("Example scenario name")
desc
Задать описание сценария:
desc("Description for scenario created as an example")
trigger
Применение:
trigger(one_user)
— при срабатывании сценария, правило, в котором используется сценарий, будет применено только к тому пользователю, для которого сработал сценарий;
trigger(all_users)
— при срабатывании сценария, правило в котором используется сценарий, будет применено ко всем пользователям, указанным в свойствах правила.
duration
Задать период активности сценария; указывается в минутах.
operation_mode
Задать режим активации сценария:
operation_mode(all)
— сценарий сработает, если выполнятся все условия;
operation_mode(any)
— сценарий сработает, если выполнится хотя бы одно из условий.
Примечание
При обновлении сценария необходимо указывать все условия: текущие условия сценария будут заменены на условия, указанные при изменении.
В качестве примера приведена настройка сценария с условием
Объём трафика
. Сценарий будет применён ко всем пользователям в течение минуты; ограничение объёма трафика: 1 ГБ/день:
Admin@UGOS# create security-policy scenarios 1 upl-rule \
... def scenario_cond scenario_cond_test
... traffic_limit(2GB) \
... period(day) \
... scond_type(traffic)
... end
... OK \
... scenario_cond = scenario_cond_test
... name(test) \
... trigger(all_users) \
... duration (1)
...
Для изменения, например, объёма трафика:
Admin@UGOS# set security-policy scenarios 3 upl-rule \
...def scenario_cond scenario_cond_test
...traffic_limit(2GB) \
...period(day) \
...scond_type(traffic)
...end
...OK \
...scenario_cond = scenario_cond_test
Условие типа Категория URL
Для создания/обновления условия типа
Категория URL
укажите:
Наименование
Описание
category
Категории или группы категорий сайтов:
category = (lib.category(URL_CATEGORY_GROUP), URL_CATEGORY_NAME)
scond_type
Тип условия:
scond_type(url_category)
count_interval
Интервал времени, за которое должно произойти заданное число срабатываний (указывается в минутах):
count_interval()
max_event_count
Количество срабатываний:
max_event_count()
Условие типа Обнаружен вирус
При настройке условия типа
Обнаружен вирус
укажите следующее:
Наименование
Описание
scond_type
Тип условия:
scond_type(virus_detection)
Условие типа Приложение
Для создания/редактирования условия типа
Приложение
используются параметры, представленные в таблице ниже:
Наименование
Описание
application
Категории приложений или группы приложений:
application = lib.applicationgroup(APP_GROUP)
или
application = lib.applicationgroup(all)
application = lib.category(APPS_CATEGORY_NAME)
scond_type
Тип условия:
scond_type(app)
count_interval
Интервал времени, за которое должно произойти заданное число срабатываний (указывается в минутах):
count_interval()
max_event_count
Количество срабатываний:
max_event_count()
Условие типа СОВ
Параметры условия типа
СОВ
Наименование
Описание
ips_tl
Уровень угрозы:
ips_tl(very_low)
– очень низкий;
ips_tl(low)
– низкий;
ips_tl(medium)
– средний;
ips_tl(high)
– высокий;
ips_tl(very_high)
– очень высокий.
scond_type
Тип условия:
scond_type(ips)
Условие типа Типы контента
Параметры условием типа
Типы контента
Наименование
Описание
response.header.Content-Type
Тип контента:
response.header.Content-Type = lib.mime(MIME_CATEGORIES_LIST)
scond_type
Тип условия:
scond_type(mime_type)
count_interval
Интервал времени, за которое должно произойти заданное число срабатываний (указывается в минутах):
count_interval()
max_event_count
Количество срабатываний:
max_event_count()
Условие типа Размер пакета
Для создания и настройки условия типа
Размер пакета
используются следующие параметры:
Наименование
Описание
packet_size
Размер пакета, при превышении которого выполняется условие; указывается следующим образом:
packet_size(1)
– размер пакета 1 байт;
packet_size(1KB)
– размер пакета 1 Кбайт;
packet_size(1MB)
– размер пакета 1 Мбайт;
packet_size(1GB)
– размер пакета 1 Гбайт.
scond_type
Тип условия:
scond_type(net_packet_size)
Условие типа Сессий с одного IP
При настройке условия типа
Сессий с одного IP
используются:
Наименование
Описание
scond_type
Тип условия:
scond_type(sessions_per_ip)
sessions_limit
Максимальное количество сессий, разрешённых с одного IP-адреса:
sessions_limit()
Условие типа Объём трафика
Чтобы задать или настроить условие типа
Объём трафика
используются следующие параметры:
Наименование
Описание
scond_type
Тип условия:
scond_type(traffic)
traffic_limit
Ограничение объёма трафика:
traffic_limit(1)
– 1 байт трафика;
traffic_limit(1KB)
– 1 Кбайт трафика;
traffic_limit(1MB)
– 1 Мбайт трафика;
traffic_limit(1GB)
– 1 Гбайт трафика.
period
Период времени:
period(minute)
– минута;
period(hour)
– час;
period(day)
– день;
period(week)
– неделя;
period(month)
– месяц.
Условие типа Проверка состояния
Для настройки условия типа
Проверка состояния
предназначены параметры:
Наименование
Описание
scond_type
Тип условия:
scond_type(health_check)
health_check_method
Метод проверки:
health_check_method(ping)
– ping;
health_check_method(dns)
– DNS-запрос;
health_check_method(get)
– HTTP-метод GET.
url.address
Адрес, на который будут выполняться ping и DNS-запрос:
url.address = "1.1.1.1"
url.domain
FQDN для проверки состояния путём выполнения DNS-запроса или URL для метода HTTP GET:
url.domain = "example.ru"
gateway
Название используемого шлюза:
gateway()
Важно!
Шлюз должен быть предварительно создан.
health_result
Результат выполнения проверки:
health_result(positive)
– положительный;
health_result(negative)
– отрицательный.
health_request_timeout
Тайм-аут подключения (в секундах):
health_request_timeout()
health_answer_timeout
Время ожидания ответа на запрос HTTP GET (в секундах):
health_answer_timeout()
health_type_request
Тип DNS-запроса:
health_type_request(a)
health_type_request(aaaa)
health_type_request(cname)
health_type_request(ns)
health_type_request(ptr)
count_interval
Интервал времени, за которое должно произойти заданное число срабатываний (указывается в минутах):
count_interval()
max_event_count
Количество срабатываний:
max_event_count()
v7.x
Настройка СОВ
Настройка правил защиты почтового трафика

## Источник

https://docs.usergate.com/nastrojka-scenariev_687.html
