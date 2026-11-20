---
заголовок: Настройка терминальных серверов
url: https://docs.usergate.com/nastrojka-terminal6nyh-serverov_2675.html
получено: 2026-11-20 16:27 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка терминальных серверов
id_статьи: 2675
обновлено: 17 Mar, 2026
ревизия: 4
---

# Настройка терминальных серверов

Technology: Identification and Authentication
Настройка терминальных серверов выполняется на уровне
users terminal-servers
Для создания терминального сервера используется команда:
Admin@nodename# create users terminal-servers <parameter>
Далее необходимо указать параметры сервера.
Параметр
Описание
enabled
Включение/отключение терминального сервера:
on;
off
name
Название терминального сервера
description
Описание терминального сервера
hosts
IP-адрес хоста. Для добавления нескольких адресов укажите их через пробел
Команда для изменения параметров терминального сервера:
Admin@nodename# set users terminal-servers <terminal-server-name> <parameter>
Команда для отображения информации о терминальном сервере:
Admin@nodename# show users terminal-servers <terminal-server-name>
Пример создания и редактирования терминального сервера:
Admin@nodename# create users terminal-servers name "Test terminal server" hosts [ 10.10.0.20 ] enabled on
Admin@nodename# show users terminal-servers "Test terminal server"
name           : Test terminal server
enabled        : on
hosts          : 10.10.0.20
Admin@nodename# set users terminal-servers "Test terminal server" description "Test terminal server description"
Admin@nodename# show users terminal-servers "Test terminal server"
name           : Test terminal server
description    : Test terminal server description
enabled        : on
hosts          : 10.10.0.20
Команда удаления терминального сервера:
Admin@nodename# delete users terminal-servers <terminal-server-name>
Также возможно удаление отдельных узлов. Для удаления необходимо уточнить их адреса:
Admin@nodename# delete users terminal-servers <terminal-server-name> hosts
v7.x
Captive-портал
Настройка профилей MFA (многофакторной аутентификации)

## Источник

https://docs.usergate.com/nastrojka-terminal6nyh-serverov_2675.html
