---
заголовок: Настройка серверов reverse-прокси
url: https://docs.usergate.com/nastrojka-serverov-reverse-proksi_244.html
источник: портал документации
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 7.0.1
раздел: Настройка серверов reverse-прокси
id_статьи: 244
обновлено: 12 Jan, 2023
ревизия: 3
---

# Настройка серверов reverse-прокси

Documentation:
Настройка серверов reverse-прокси производится на уровне
global-portal reverse-proxy-servers
Для создания сервера reverse-прокси используется следующая команда:
Admin@UGOS# create global-portal reverse-proxy-servers
Доступно указание следующих параметров:
Параметр
Описание
name
Название сервера reverse-прокси.
description
Описание сервера reverse-прокси.
address
Адрес или домен сервера reverse-прокси.
port
TCP-порт сервера reverse-прокси.
https
Использование протокола HTTPS до публикуемого сервера:
: использовать.
off
: не использовать.
check-cert
Проверка валидности SSL-сертификата, установленного на публикуемом сервере:
: проверять.
off
: не проверять.
keep-source-ip
Использование оригинального IP-адреса источника в пакетах, пересылаемых на публикуемый сервер:
: оставить оригинальный IP-адрес источника.
off
: заменить IP-адрес источника на IP-адрес UserGate.
Следующая команда предназначена для обновления параметров сервера reverse-прокси:
Admin@UGOS# set global-portal reverse-proxy-servers <server-name>
Параметры, которые могут быть обновлены, аналогичны с параметрами команды для добавления нового сервера.
Структура команды для удаления сервера:
Admin@UGOS# delete global-portal reverse-proxy-servers <server-name>
Структура команды для отображения информации о сервере reverse-прокси:
Admin@UGOS# show global-portal reverse-proxy-servers <server-name>
v7.x
Настройка правил reverse-прокси
Настройка удалённого доступа (VPN)

## Источник

https://docs.usergate.com/nastrojka-serverov-reverse-proksi_244.html
