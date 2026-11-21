---
заголовок: Настройка WebSocket-профилей
url: https://docs.usergate.com/nastrojka-websocket-profilej_3017.html
источник: портал документации
получено: 2026-11-20 16:27 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка WebSocket-профилей
id_статьи: 3017
обновлено: 28 Apr, 2026
ревизия: 3
---

# Настройка WebSocket-профилей

Technology: WAF
Настройка WebSocket-профилей происходит на уровне
websocket-profiles
Для создания WebSocket-профилей используется следующая команда:
Admin@nodename# create security-policy websocket-profiles <parameter>
Далее необходимо задать следующие параметры.
Параметр
Описание
name
Название WebSocket-профиля
description
Описание WebSocket-профиля
block
Включение/отключение блокирования любого WebSocket-трафика, который приходит в UserGate WAF:
Off
check-request
Проверка целостности handshake-запроса:
Off
log
Включение/отключение журналирования событий:
Off
check-origin
Проверка наличия в запросе заголовка
Origin
Off
origin
Добавление списка URL источников, с которыми разрешается устанавливать WebSocket-соединение. Подробнее о создании списков URL в разделе — «
Настройка списков URL
origin-negate
Добавление списка URL нежелательных источников. WebSocket-соединения с ними будут игнорироваться
check-extension
Включение/отключение проверки расширений в заголовке
Sec-WebSocket-Extensions
Off
extension
Добавление списка разрешенных расширений. WebSocket-соединения будут устанавливаться только по тем запросам, в заголовках которых указаны разрешенные расширения
extension-negate
Инвертация проверки по списку, указанному в параметре
extension
Off
WebSocket-соединения по запросам, в заголовках которых указаны расширения из списка, будут игнорироваться
check-protocol
Включение/отключение проверки субпротоколов в заголовке
Sec-WebSocket-Protocols
Off
protocol
Добавление списка разрешенных субпротоколов. WebSocket-соединения будут устанавливаться только по тем запросам, в заголовках которых указаны разрешенные субпротоколы
protocol-negate
Инвертация проверки по списку, указанному в параметре
protocol
Off
WebSocket-соединения по запросам, в заголовках которых указаны субпротоколы из списка, будут игнорироваться
Команда для редактирования параметров WebSocket-профиля:
Admin@nodename# set security-policy websocket-profiles <websocket-profile_name> <parameter>
Команда для отображения информации о всех WebSocket-профилях:
Admin@nodename# show security-policy websocket-profiles
Команда для отображения информации об определенном WebSocket-профиле:
Admin@nodename# show security-policy websocket-profiles <profile_name>
Команда для удаления существующего WebSocket-профиля используется следующая команда:
Admin@nodename# delete security-policy websocket-profiles <profile_name>
Настройка профиля ответа
UserGate Policy Language (UPL)

## Источник

https://docs.usergate.com/nastrojka-websocket-profilej_3017.html
