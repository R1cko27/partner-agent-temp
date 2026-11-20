---
заголовок: Настройка подключения к серверу регистрации доверенных браузеров
url: https://docs.usergate.com/nastrojka-podklyucheniya-k-serveru-registracii-doverennyh-brauzerov_2882.html
получено: 2026-11-20 16:27 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка подключения к серверу регистрации доверенных браузеров
id_статьи: 2882
обновлено: 17 Mar, 2026
ревизия: 4
---

# Настройка подключения к серверу регистрации доверенных браузеров

Technology: Identification and Authentication
Подключение к серверу регистрации доверенных браузеров настраиваются на уровне
users trusted-browser
Для создания подключения используется команда:
Admin@nodename# create users trusted-browser <parameter>
Далее необходимо указать параметры подключения.
Параметр
Описание
name
Название подключения
description
Описание подключения
url
URL сервера регистрации доверенных браузеров, развернутого в компании
jwt-issuer
Параметр задается администратором в переменных среды сервера регистрации Яндекс Браузера (URL_IDP) и передается в составе токена JWT. Используется для идентификации сервера регистрации, выдавшего JWT, если в сети имеется нескольких таких серверов
port
Порт подключения к серверу регистрации доверенных браузеров
bearer-token
Ключ доступа к серверу регистрации доверенных браузеров. Определяется администратором сервиса регистрации
keys-update-timeout
Интервал времени, через который UserGate SWG запрашивает у сервера регистрации доверенных браузеров набор открытых ключей в формате JWKS
Команда для изменения параметров подключения:
Admin@nodename# set users trusted-browser <connection-name> <parameter>
Для обновления доступен список параметров, аналогичный списку параметров команды
create
Команда для просмотра параметров подключения к серверу регистрации доверенных браузеров:
Admin@nodenamet# show users trusted-browser <connection-name>
Пример создания и редактирования подключения к серверу регистрации доверенных браузеров:
Admin@nodename# create users trusted-browser name "Test1" description "New enrollment host connection" url https://test1.net jwt-issuer https://test1.net bearer-token 123321 port 8080
Admin@nodename# show users trusted-browser Test1
name                   : Test1
description            : New enrollment host connection
url                    : https://test1.net
jwt-issuer             : https://test1.net
port                   : 8080
bearer-token           : 123321
keys-update-timeout    : 600
Команда для удаления подключения к серверу регистрации:
Admin@nodename# delete users trusted-browser <connection-name>
Подробнее о работе с доверенными браузерами — в разделе «
Работа с доверенными браузерами
Об использовании доверенных браузеров в правилах фильтрации контента — в разделе «
Настройка фильтрации контента
»; в правилах reverse-прокси — в разделе «
Настройка правил reverse-прокси
v7.x
Настройка применения политик к пользователям
Настройка раздела Политики сети

## Источник

https://docs.usergate.com/nastrojka-podklyucheniya-k-serveru-registracii-doverennyh-brauzerov_2882.html
