---
заголовок: Настройка правил reverse-прокси
url: https://docs.usergate.com/nastrojka-pravil-reverse-proksi_1861.html
получено: 2026-11-20 16:25 +0700
продукт: WAF
версия: 7.x
раздел: Настройка правил reverse-прокси
id_статьи: 1861
обновлено: 15 Sep, 2025
ревизия: 8
---

# Настройка правил reverse-прокси

Правила reverse-прокси в интерфейсе командной строки настраиваются на уровне
global-portal reverse-proxy-rules
. Подробнее о структуре команд — в разделе
UserGate Policy Language
Структура команды для создания правила reverse-прокси:
Admin@nodename# create global-portal reverse-proxy-rules <position> upl-rule <parameters>
Параметры настройки правил reverse-прокси:
Параметр
Описание
Действие для создания правила с помощью UPL
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
— включение;
enabled(no)
или
enabled(false)
— отключение
name
Название правила reverse-прокси.
Например,
name("Reverse proxy rule example")
desc
Описание правила.
Например,
desc("Reverse proxy rule example set via CLI")
profile
Сервер reverse-прокси, куда WAF будет пересылать запросы.
Для указания сервера:
profile("Reverse proxy server example")
url.port
Порт, на котором WAF будет слушать входящие запросы.
Например,
url.port = 80
is_https
Поддержка HTTPS:
is_https(yes)
или
is_https(true)
— использовать HTTPS;
is_https(no)
или
is_https(false)
— не использовать HTTPS.
ssl_profile
Профиль SSL; указывается при использовании HTTPS:
ssl_profile("Default SSL profile")
Подробнее о работе с профилями SSL через CLI — в разделе «
Настройка профилей SSL
certificate
Сертификат, используемый для поддержки HTTPS-соединения.
Указывается при использовании HTTPS:
certificate("Certificate example")
cert_auth_enabled
Аутентификация по сертификату:
cert_auth_enabled(yes)
или
cert_auth_enabled(true)
— включить авторизацию по сертификату;
cert_auth_enabled(no)
или
cert_auth_enabled(false)
— отключить авторизацию по сертификату
src.zone
Зона источника трафика.
Для указания зоны источника, например Untrusted:
src.zone = Untrusted
Подробнее о настройке зон с использованием интерфейса командной строки — в разделе «
Зоны
src.ip
Добавление списков IP-адресов или доменов источника.
Для указания списка IP-адресов:
src.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для указания списка доменов источника:
src.ip = lib.url()
; в скобках необходимо указать название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
src.geoip
Указание GeoIP источника; необходимо указать код страны (например,
src.geoip = RU
Коды названий стран доступны по ссылке:
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15
user
Пользователи и группы пользователей, для которых применяется правило reverse-прокси. Добавление пользователей доступно только при использовании авторизации по сертификату.
Для добавления LDAP групп и пользователей необходим корректно настроенный LDAP-коннектор (подробнее о настройке LDAP-коннектора через CLI — в разделе «
Настройка LDAP-коннектора
»).
Пример добавления локальных пользователя (local_user) и группы (Local Group), пользователя (example.local\AD_user) и группы LDAP (AD group):
user = (local_user, "CN=Local Group, DC=LOCAL", "example.loc\\AD_user", "CN=AD group, OU=Example, DC= example, DC=loc")
Заранее был настроен домен Active Directory example.loc. При добавлении пользователей и групп LDAP можно указать список путей на сервере, начиная с которых система будет осуществлять поиск пользователей и групп
dst.ip
Один из внешних IP-адресов WAF, доступный из сети интернет, куда адресован трафик внешних клиентов.
Для указания списка IP-адресов:
dst.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для указания списка доменов назначения:
dst.ip = lib.url()
; в скобках необходимо указать название URL-списка, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
dst.geoip
Указание GeoIP; необходимо указать код страны (например,
dst.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15
request.header.User-Agent
Useragent пользовательских браузеров, для которых будет применено данное правило.
Для указания Useragent пользовательских браузеров:
request.header.User-Agent = lib.useragent()
; в скобках необходимо указать название категории Useragent браузеров.
Подробнее о создании и настройке собственных списков с использованием интерфейса командной строки — в разделе «
Настройка Useragent браузеров
rewrite_path
Подмена домена и/или пути в URL-запросе пользователя.
Например, для преобразования запросов, приходящих на http://www.example.com/path1 в http://www.example.loc/path2 нужно указать:
rewrite_path("http://www.example.com/path1", "http://www.example.loc/path2")
waf_profile
Включение защиты веб-приложений в правиле reverse-прокси.
Необходимо указать заранее созданный WAF-профиль.
Например,
waf_profile("Example WAF profile")
Подробнее о создании и настройке WAF-профилей с использованием интерфейса командной строки — в разделе «
Настройки безопасности WAF в CLI
websocket_profile
Включение обработки websocket-соединений (доступно в версии ПО 7.4.1 и выше).
Необходимо указать заранее созданный websocket-профиль.
Например,
websocket_profile("Example websocket profile")
Подробнее о создании и настройке WAF-профилей с использованием интерфейса командной строки — в разделе «
Настройка WebSocket-профилей в CLI
Для редактирования правила reverse-прокси используется команда:
Admin@nodename# set global-portal reverse-proxy-rules <position> upl-rule <parameters>
Для просмотра параметров правила reverse-прокси используется команда:
Admin@nodename# show global-portal reverse-proxy-rules <position>
Пример создания правила reverse-прокси:
Admin@nodename# create global-portal reverse-proxy-rules 1 upl-rule OK \
...url.port = 80 \
...src.zone = Untrusted \
...profile("Reverse proxy server1") \
...rewrite_path("example.com/path1", "example.local/path2") \
...waf_profile("Example WAF profile") \
...name("Test reverse proxy rule") \
...desc("Test reverse proxy rule description") \
...enabled(true)
...
Admin@nodename# show global-portal reverse-proxy-rules 1
% ----------------- 1 -----------------
OK \
url.port = 80 \
src.zone = Untrusted \
desc("Test reverse proxy rule description") \
profile("Reverse proxy server1") \
rewrite_path("example.com/path1", "example.local/path2") \
waf_profile("Example WAF profile") \
enabled(true) \
id("7dc7041a-6538-400b-8f1e-9b18287218ac") \
name("Test reverse proxy rule")
Для удаления правила reverse-прокси используется команда:
Admin@nodename# delete global-portal reverse-proxy-rules <position>
v7.x
Настройка серверов reverse-прокси
Настройки безопасности

## Источник

https://docs.usergate.com/nastrojka-pravil-reverse-proksi_1861.html
