---
заголовок: Процедура перехода с UserGate 5 на UserGate 6
url: https://docs.usergate.com/procedura-perehoda-s-usergate-5-na-usergate-6_51.html
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 5.x, 6.1.8, 6.1.9
раздел: Процедура перехода с UserGate 5 на UserGate 6
id_статьи: 51
обновлено: 20 Aug, 2025
ревизия: 10
---

# Процедура перехода с UserGate 5 на UserGate 6

Скачать update для UserGate 5 по ссылке:
https://static.usergate.com/tools/api5beam.zip
Если установлен UserGate версии utm-5.0.6.4729R или ниже — установить update из папки update_old_key.
Если установленная версия UserGate utm-5.0.6.4825R или выше, то установить update из папки update_new_key.
Загрузить его через веб-консоль UserGate и выполнить установку.
Включить сервис XML-RPC на зоне интерфейса, с которого предполагается выгрузка данных.
Для этого нужно выполнить запрос в браузере (указать IP-адрес интерфейса UserGate 5): https://<X.X.X.X>:8001?features=zone-xml-rpc и включить сервис XML-RPC для управления на нужной зоне.
Загрузить архив
ug_ngfw_converter.zip
Архив доступен по ссылке:
https://docs.usergate.com/konvertery-konfiguracij-722/
. Архив необходимо распаковать и сделать файл
ug_ngfw_converter
исполняемым.
Экспортировать данные с UserGate 5.
Примечание
В момент выгрузки данных LDAP-сервер и DNS должны быть доступны с устройства UserGate 5.
Для выгрузки данных в терминале необходимо запустить скрипт
ug_ngfw_converter
, ввести данные для подключения и выполнить экспорт данных (инструкция по работе скрипта:
https://github.com/usergate/Migrations/tree/main/ug_ngfw_converter
Развернуть образ UserGate 6.
После окончания установки UserGate 6 выполнить настройку DNS и LDAP-коннектора.
Выполнить импорт данных на UserGate 6.
Для импорта данных нужно запустить в терминале скрипт
ug_ngfw_converter
, ввести данные для подключения и выполнить импорт данных (инструкция по работе скрипта:
https://github.com/usergate/Migrations/tree/main/ug_ngfw_converter
v5.x
v6.x
Обновление ПАК с внешнего USB-носителя
Процесс перехода на UserGate версии 7.x

## Источник

https://docs.usergate.com/procedura-perehoda-s-usergate-5-na-usergate-6_51.html
