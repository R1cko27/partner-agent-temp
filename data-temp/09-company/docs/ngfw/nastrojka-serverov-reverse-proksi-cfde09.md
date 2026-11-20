---
заголовок: Настройка серверов reverse-прокси
url: https://docs.usergate.com/nastrojka-serverov-reverse-proksi_839.html
источник: портал документации
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка серверов reverse-прокси
id_статьи: 839
обновлено: 18 Nov, 2025
ревизия: 6
---

# Настройка серверов reverse-прокси

Documentation:
Настройка серверов reverse-прокси производится на уровне
global-portal reverse-proxy-servers
Для создания сервера reverse-прокси используется следующая команда:
Admin@nodename# create global-portal reverse-proxy-servers <parameter>
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
keep-source-ip
Использование оригинального IP-адреса источника в пакетах, пересылаемых на публикуемый сервер:
: оставить оригинальный IP-адрес источника.
off
: заменить IP-адрес источника на IP-адрес UserGate.
Важно!
Если в пакетах сохраняется оригинальный IP-адрес источника, для корректной работы необходимо настроить маршрутизацию таким образом, чтобы веб-сервер отвечал через тот же сетевой интерфейс UG NGFW, с которого приходят запросы клиентов. Для этого на веб-сервере в качестве шлюза по умолчанию можно указать UG NGFW или можно настроить статические маршруты через UG NGFW для «белых» IP-адресов источников.
Команда для редактирования параметров сервера reverse-прокси:
Admin@nodename# set global-portal reverse-proxy-servers <server-name> <parameter>
Параметры, которые могут быть обновлены, аналогичны с параметрами команды для добавления нового сервера.
Структура команды для отображения информации о сервере reverse-прокси:
Admin@nodename# show global-portal reverse-proxy-servers <server-name>
Структура команды для удаления сервера:
Admin@nodename# delete global-portal reverse-proxy-servers <server-name>
v7.x
Настройка правил reverse-прокси
Настройка VPN в CLI

## Источник

https://docs.usergate.com/nastrojka-serverov-reverse-proksi_839.html
