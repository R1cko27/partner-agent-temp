---
заголовок: Настройка серверов reverse-прокси
url: https://docs.usergate.com/nastrojka-serverov-reverse-proksi_2691.html
источник: портал документации
получено: 2026-11-20 16:27 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка серверов reverse-прокси
id_статьи: 2691
обновлено: 23 Mar, 2026
ревизия: 6
---

# Настройка серверов reverse-прокси

Серверы reverse-прокси настраиваются на уровне
global-portal reverse-proxy-servers
Для создания сервера reverse-прокси используется команда:
Admin@nodename# create global-portal reverse-proxy-servers <parameter>
Параметры сервера reverse-прокси.
Параметр
Описание
name
Название сервера reverse-прокси
description
Описание сервера reverse-прокси
address
Адрес или домен публикуемого сервера
port
TCP-порт публикуемого сервера
https
Использование протокола HTTPS до публикуемого сервера:
— использовать;
off
— не использовать
keep-source-ip
Использование оригинального IP-адреса источника в пакетах, пересылаемых на публикуемый сервер:
— оставить оригинальный IP-адрес источника;
off
— заменить IP-адрес источника на IP-адрес UserGate.
Важно!
Если в пакетах сохраняется оригинальный IP-адрес источника, для корректной работы необходимо настроить маршрутизацию таким образом, чтобы веб-сервер отвечал через тот же сетевой интерфейс UserGate SWG, с которого приходят запросы клиентов. Для этого на веб-сервере в качестве шлюза по умолчанию можно указать UserGate SWG или можно настроить статические маршруты через UserGate SWG для «белых» IP-адресов источников
Команда для редактирования параметров сервера reverse-прокси:
Admin@nodename# set global-portal reverse-proxy-servers <server-name> <parameter>
Параметры, которые могут быть обновлены, аналогичны с параметрами команды для добавления нового сервера reverse-прокси.
Команда для отображения информации о сервера reverse-прокси:
Admin@nodename# show global-portal reverse-proxy-servers <server-name>
Команда для удаления сервера reverse-прокси:
Admin@nodename# delete global-portal reverse-proxy-servers <server-name>
v7.x
Настройка правил reverse-прокси
Настройка библиотек

## Источник

https://docs.usergate.com/nastrojka-serverov-reverse-proksi_2691.html
