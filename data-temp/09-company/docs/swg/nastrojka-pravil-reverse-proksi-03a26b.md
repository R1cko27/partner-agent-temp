---
заголовок: Настройка правил reverse-прокси
url: https://docs.usergate.com/nastrojka-pravil-reverse-proksi_2690.html
источник: портал документации
получено: 2026-11-20 16:27 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка правил reverse-прокси
id_статьи: 2690
обновлено: 23 Mar, 2026
ревизия: 9
---

# Настройка правил reverse-прокси

Правила reverse-прокси настраиваются на уровне
global-portal reverse-proxy-rules
с помощью синтаксиса UPL Подробнее о структуре команд — в разделе «
UserGate Policy Language
Для создания правила reverse-прокси используется команда:
Admin@nodename# create global-portal reverse-proxy-rules <position> upl-rule <parameters>
Параметры настройки правил reverse-прокси.
Параметр
Описание
Действие для создания правила с помощью UPL
enabled
Включение или отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила reverse-прокси.
Например:
name("Reverse proxy rule example")
desc
Описание правила.
Например:
desc("Reverse proxy rule example set via CLI")
profile
Сервер reverse-прокси, на который UserGate SWG будет пересылать запросы.
Для указания сервера reverse-прокси:
profile("Reverse proxy server example")
url.port
Порт, на котором узел UserGate SWG будет слушать входящие запросы, например,
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
— не использовать HTTPS
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
Для списка IP-адресов:
src.ip = lib.network()
; в скобках укажите название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для списка доменов источника:
src.ip = lib.url()
; в скобках укажите название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
src.geoip
Указание GeoIP источника; необходимо указать код страны (например,
src.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
user
Пользователи и группы пользователей, для которых применяется правило reverse-прокси. Добавление пользователей доступно только при использовании авторизации по сертификату.
Для добавления LDAP-групп и пользователей необходим корректно настроенный LDAP-коннектор (о настройке LDAP-коннектора через CLI — в разделе «
Настройка LDAP-коннектора
»).
Примеры добавления локальных пользователя (local_user) и группы (Local Group), пользователя (example.local\AD_user) и группы LDAP (AD group):
user = (local_user, "CN=Local Group, DC=LOCAL", "example.loc\\AD_user", "CN=AD group, OU=Example, DC= example, DC=loc")
Заранее был настроен домен Active Directory example.loc. При добавлении пользователей и групп LDAP можно указать список путей на сервере, начиная с которых система будет осуществлять поиск пользователей и групп
dst.ip
Один из внешних IP-адресов устройства UserGate, доступный из сети интернет, куда адресован трафик внешних клиентов.
Для списка IP-адресов:
dst.ip = lib.network()
; в скобках укажите название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для списка доменов назначения:
dst.ip = lib.url()
; в скобках укажите название URL-списка, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
dst.geoip
Указание GeoIP; необходимо указать код страны (например,
dst.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
request.header.User-Agent
User agent пользовательских браузеров, для которых будет применено данное правило.
Для указания User agent пользовательских браузеров:
request.header.User-Agent = lib.useragent()
; в скобках необходимо указать название категории User agent браузеров.
Подробнее о создании и настройке собственных списков с использованием интерфейса командной строки читайте в разделе
Настройка Usera gent браузеров
rewrite_path
Подмена домена или пути в URL в запросе пользователя. Например, позволяет преобразовать запросы, приходящие на http://www.example.com/path1 в http://www.example.loc/path2. Для этого укажите:
rewrite_path("http://www.example.com/path1", "http://www.example.loc/path2")
trusted_browser
Проверка подлинности браузера для предоставления доступа к ресурсам. Укажите созданное ранее подключение к серверу регистрации доверенных браузеров.
Например:
trusted_browser = "111"
Подробнее о работе с доверенными браузерами — в разделе «
Работа с доверенными браузерами
proxy_pass_x_forwarded
Добавление или перезапись следующих дополнительных HTTP-заголовков:
X-Forwarded-Host
: содержит значение заголовка Host из исходного запроса. Это значение требуется внутреннему веб-серверу для уточнения, какой контент следует вернуть клиенту, а также при журналировании и балансировке нагрузки.
X-Forwarded-Proto
: содержит сведения о протоколе исходного запроса, которые позволяют на стороне внутреннего веб-сервера выполнять переадресацию на безопасный ресурс либо генерировать корректные ссылки.
X-Forwarded-Port
: передает исходный порт подключения клиента, который необходим для генерации корректных ссылок на стороне внутреннего веб-сервера.
Например:
proxy_pass_x_forwarded(proto, host, port)
Подробнее о работе с дополнительными HTTP-заголовками — в разделе «
Публикация ресурсов с помощью правил reverse-прокси
Команда для редактирования правила reverse-прокси:
Admin@nodename# set global-portal reverse-proxy-rules <position> upl-rule <parameters>
Команда для просмотра параметров правила reverse-прокси:
Admin@nodename# show global-portal reverse-proxy-rules <position>
Пример создания правила reverse-прокси:
Admin@nodename# create global-portal reverse-proxy-rules 1 upl-rule OK \
...url.port = 80 \
...src.zone = Untrusted \
...profile("Reverse proxy server1") \
...rewrite_path("example.com/path1", "example.local/path2") \
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
enabled(true) \
id("7dc7041a-6538-400b-8f1e-9b18287218ac") \
name("Test reverse proxy rule")
Команда для удаления правила reverse-прокси:
Admin@nodename# delete global-portal reverse-proxy-rules <position>
v7.x
Настройка веб-портала
Настройка серверов reverse-прокси

## Источник

https://docs.usergate.com/nastrojka-pravil-reverse-proksi_2690.html
