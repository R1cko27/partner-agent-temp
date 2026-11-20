---
заголовок: Настройка терминальных серверов
url: https://docs.usergate.com/nastrojka-terminal6nyh-serverov_814.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка терминальных серверов
id_статьи: 814
обновлено: 26 Mar, 2024
ревизия: 4
---

# Настройка терминальных серверов

Documentation:
Technology: Identification and Authentication
В данном разделе описана настройка терминальных серверов с использованием интерфейса командной строки. Настройка производится на уровне
users terminal-servers
Для создания терминального сервера необходимо ввести следующую команду:
Admin@nodename# create users terminal-servers <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
enabled
Включение/отключение терминального сервера:
off
name
Название терминального сервера.
description
Описание терминального сервера.
hosts
IP-адрес хоста. Для добавления нескольких адресов укажите их через пробел.
Команда для редактирования параметров (параметры приведены выше в таблице) терминального сервера:
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
Также возможно удаление отдельных хостов. Для удаления необходимо уточнить их адреса:
Admin@nodename# delete users terminal-servers <terminal-server-name> hosts
v7.x
Captive-портал
Настройка профилей MFA (мультифакторной аутентификации)

## Источник

https://docs.usergate.com/nastrojka-terminal6nyh-serverov_814.html
