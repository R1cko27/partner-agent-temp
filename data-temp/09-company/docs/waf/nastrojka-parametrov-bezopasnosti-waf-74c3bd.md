---
заголовок: Настройка параметров безопасности WAF
url: https://docs.usergate.com/nastrojka-parametrov-bezopasnosti-waf_3015.html
получено: 2026-11-20 16:26 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка параметров безопасности WAF
id_статьи: 3015
обновлено: 28 Apr, 2026
ревизия: 5
---

# Настройка параметров безопасности WAF

Содержание:
Technology: WAF
Настройка персональных слоев
Персональные WAF-слои настраиваются на уровне
waf custom-layers
с использованием языка описания политик UPL. Подробнее о структуре команд — в разделе «
UserGate Policy Language
Для создания персонального слоя используется команда:
Admin@nodename# create waf custom-layers name <custom_layer_name> description <description> upl-rule
Команда для изменения параметров персонального слоя:
Admin@nodename# set waf custom-layers <custom_layer_name> upl-rule
Команда для отображения информации о всех персональных слоях:
Admin@nodename# show waf custom-layers
Команда для отображения информации об определенном персональном слое:
Admin@nodename# show waf custom-layers <custom_layer_name>
Пример создания тестового персонального слоя с использованием UPL:
Admin@nodename# create waf custom-layers name "Layer 2" upl-rule DENY src.ip = lib.network("Bad ips", "Test ips")
DENY dst.ip = lib.network("Bad ips")
PASS request.header.User-Agent = lib.useragent(Browsers)
DENY time = lib.time(Weekends)
Admin@nodename#
Admin@nodename# show waf custom-layers "Layer 2"
name        : Layer 2
upl-rule    : DENY src.ip = lib.network("Bad ips", "Test ips")
DENY dst.ip = lib.network("Bad ips")
PASS request.header.User-Agent = lib.useragent(Browsers)
DENY time = lib.time(Weekends)
Admin@nodename#
Команда для удаления существующего персонального слоя:
Admin@nodename# delete waf custom-layers <custom_layer_name>
Настройка WAF-профилей
WAF-профили настраиваются на уровне
waf profiles
Для создания WAF-профиля используется команда:
Admin@nodename# create waf profiles name <profile_name> description <description> enable-layers [ layer_1 layer_2 layer_n ]
Команда для изменения параметров WAF-профиля:
Admin@nodename# set waf profiles <profile_name> name <new_name> description <new_description> enable-layers [ list of layers to enable ] system <change_system_layer>
Команда для изменения профиля ответа в WAF-профиле:
Admin@nodename# set waf profiles
system
overridden-rules rules-names [ "#RefRef DoS tool (1)" "#RefRef DoS tool (2)" ] response-profile <tab>
По умолчанию выбрано значение
Do not use
. Другие значения станут доступны после того, как будут созданы профили ответов.
Команда для отображения информации о всех WAF-профилях:
Admin@nodename# show waf profiles
Команда для изменения размера анализируемого тела запроса/ответа:
set waf profiles ProfileName max-body-inspection-size 200000
Команда для отображения информации об определенном WAF-профиле:
Admin@nodename# show waf profiles <profile_name>
Пример создания WAF-профиля:
Admin@nodename# create waf profiles name "Test profile 1" description "Test profile #1" enable-layers [ "Layer 4 (custom)" "HTTP Constraint" ]
Admin@nodename#
Admin@nodename# show waf profiles "Test profile 1"
name             : Test profile 1
description      : Test profile #1
enable-layers    : Layer 4 (custom); HTTP Constraint
Admin@nodename#
Команда для удаления существующего WAF-профиля:
Admin@nodename# delete waf profiles <profile_name>
Настройка параметров системных WAF-правил
Параметры системных WAF-правил настраиваются на уровне
waf system-rules
У системных WAF-правил могут быть изменены следующие параметры:
состояние (
enabled
) —
on/off
журналирование (
enable-logging
) —
on/off
действие (
action
) —
pass, deny, force-pass, force-deny
профиль ответа (
response-profile
) —
do not use
<response-profile name>
Пример команды настройки системного WAF-правила:
Admin@nodename# set waf system-rules rules ["#RefRef DoS tool (1)"] enabled on enable-logging on action deny
response-profile "<response-profile name>"
В квадратных скобках указывается название одного или нескольких системных WAF-правил, к которым применяются изменения параметров. Названия WAF-правил указываются в кавычках и разделяются пробелами.
Пример команды изменения параметров нескольких системных WAF-правил:
Admin@oulineeladin# set waf system-rules rules ["#RefRef DoS tool (1)" "#RefRef DoS tool (2)"] enabled off
Команда для отображения информации о всех системных WAF-правилах:
Admin@nodename# show waf system-rules
Пример отображения информации об определенном системном WAF-правиле:
Admin@oulineeladin# show waf system-rules "#RefRef DoS tool (1)"
name              : #RefRef DoS tool (1)
enabled           : on
action            : deny
description       : This event is trigerred when a malicious/suspicious user-agent is detected in the request.
reference         : https://www.owasp.org/index.php/Denial_of_Service
threat-level      : medium
technology        : All systems
layer             : Denial of Service
enable-logging    : on
last-update       : 2016-03-17T00:00Z
response-profile  : Do not use
Просмотр системных WAF-слоев
Команда для отображения информации об имеющихся системных WAF-слоях:
Admin@nodename# show waf system-layers
Команда для отображения информации о конкретном системном WAF-слое:
Admin@minhanhicont# show waf system-layers <system_layer_name>
v7.x
Настройка безопасности
Настройка профиля ответа

## Источник

https://docs.usergate.com/nastrojka-parametrov-bezopasnosti-waf_3015.html
