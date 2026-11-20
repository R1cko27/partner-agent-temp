---
заголовок: Настройка серверов аутентификации
url: https://docs.usergate.com/nastrojka-serverov-autentifikacii_1706.html
источник: портал документации
получено: 2026-11-20 16:25 +0700
продукт: DCFW
версия: 8.x
раздел: Настройка серверов аутентификации
id_статьи: 1706
обновлено: 19 Nov, 2024
ревизия: 3
---

# Настройка серверов аутентификации

Содержание:
Раздел
Серверы аутентификации
позволяет произвести настройку LDAP-коннектора, серверов RADIUS, TACACS+, NTLM, SAML IDP. Настройка серверов аутентификации производится на уровне
users auth-server
и будет рассмотрена далее в соответствующих разделах.
Настройка LDAP-коннектора
Настройка LDAP-коннектора производится на уровне
users auth-server ldap
Для создания LDAP-коннектора используется команда:
Admin@nodename# create users auth-server ldap <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя LDAP-коннектора.
enabled
Включение/отключение сервера аутентификации.
description
Описание LDAP-коннектора.
ssl
Определяет:
— использование SSL-соединения для подключения к LDAP-серверу.
off
— подключение к LDAP-серверу без использования SSL-соединения.
address
IP-адрес контроллера или название домена LDAP.
bind-dn
Имя пользователя, которое будет использоваться для подключения к серверу; указывается в формате DOMAIN\username или username
domain. Пользователь должен быть заведён в домене.
password
Пароль пользователя для подключения к домену.
cache-ttl
Время жизни записей LDAP-кэша. (Опция доступна начиная с релиза UGOS 7.1.3).
domains
Список доменов, которые обслуживаются указанным контроллером домена.
search-roots
Список путей в сервере LDAP, начиная с которых система будет осуществлять поиск пользователей и групп. Необходимо указывать полное имя, например, ou=Office,dc=example,dc=com. Если пути поиска не указаны, то поиск производится по всему каталогу, начиная от корня.
Для редактирования информации о существующем LDAP-коннекторе используется команда:
Admin@nodename# set users auth-server ldap <ldap-server-name> <parameter>
Параметры, доступные для обновления, аналогичны параметрам создания LDAP-коннектора.
Команда для отображения информации о LDAP-коннекторе:
Admin@nodename# show users auth-server ldap <ldap-server-name>
Примеры команд создания и редактирования LDAP-коннектора:
Admin@nodename# create users auth-server ldap name "New LDAP connector" ssl on address 10.10.0.10 bind-dn ug@testd.local password 12345 domains [ testd.local ] search-roots [ dc=testd,dc=local ] enabled on
Admin@nodename# show users auth-server ldap "New LDAP connector"
name             : New LDAP connector
enabled          : on
ssl              : on
address          : 10.10.0.10
bind-dn          : ug@testd.local
domains          : testd.local
search-roots     : dc=testd,dc=local
keytab_exists    : off
Admin@nodename# set users auth-server ldap "New LDAP connector" description "New LDAP connector description"
Admin@nodename# show users auth-server ldap "New LDAP connector"
name             : New LDAP connector
description      : New LDAP connector description
enabled          : on
ssl              : on
address          : 10.10.0.10
bind-dn          : ug@testd.local
domains          : testd.local
search-roots     : dc=testd,dc=local
keytab_exists    : off
Для удаления LDAP-коннектора используется команда:
Admin@nodename# delete users auth-server ldap <ldap-server-name> <parameter>
Также возможно удаления отдельных параметров LDAP-коннектора. Для удаления доступны следующие параметры:
domains
search-roots
Настройка RADIUS-сервера
Настройка RADIUS-сервера производится на уровне
users auth-server radius
Для создания сервера аутентификации RADIUS используется команда со следующей структурой:
Admin@nodename# create users auth-server radius <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя RADIUS-сервера.
enabled
Включение/отключение сервера аутентификации.
description
Описание сервера аутентификации.
secret
Общий ключ, используемый протоколом RADIUS для аутентификации.
addresses
IP-адрес и UDP-порт, на котором сервер RADIUS слушает запросы (по умолчанию порт 1812); указывается в формате <ip:port>.
Команда для обновления информации о сервере RADIUS:
Admin@nodename# set users auth-server radius <radius-server-name> <parameter>
Параметры, которые могут быть обновлены, соответствуют параметрам, указание которых возможно при создании сервера аутентификации.
Команда для отображения информации о RADIUS-сервере:
Admin@nodename# show users auth-server radius <radius-server-name>
Примеры команд создания и редактирования RADIUS-сервера:
Admin@nodename# create users auth-server radius name "New RADIUS server" addresses [ 10.10.0.9:1812 ] secret 12345 enabled on
Admin@nodename# show users auth-server radius "New RADIUS server"
name           : New RADIUS server
enabled        : on
addresses      :
host    : 10.10.0.9
port    : 1812
Admin@nodename# set users auth-server radius "New RADIUS server" description "New RADIUS server description"
Admin@nodename# show users auth-server radius "New RADIUS server"
name           : New RADIUS server
description    : New RADIUS server description
enabled        : on
addresses      :
host    : 10.10.0.9
port    : 1812
Для удаления сервера:
Admin@nodename# delete users auth-server radius <radius-server-name> <parameter>
Также возможно удаления отдельных параметров RADIUS-сервера. Для удаления доступны следующие параметры:
addresses
Настройка сервера TACACS+
Настройка сервера TACACS+ производится на уровне
users auth-server tacacs
Для создания сервера аутентификации TACACS+ используется команда со следующей структурой:
Admin@nodename# create users auth-server tacacs <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя сервера TACACS+.
enabled
Включение/отключение сервера.
description
Описание сервера аутентификации.
secret
Общий ключ, используемый протоколом TACACS+ для аутентификации.
address
IP-адрес сервера TACACS+.
port
UDP-порт, на котором сервер TACACS+ слушает запросы на аутентификацию. По умолчанию это порт UDP 1812.
single-connection
Использовать одно TCP-соединение для работы с сервером TACACS+.
timeout
Время ожидания сервера TACACS+ для получения аутентификации. По умолчанию 4 секунды.
Команда для редактирования информации о сервере TACACS+:
Admin@nodename# set users auth-server tacacs <tacacs-server-name> <parameter>
Параметры, которые могут быть обновлены, соответствуют параметрам, указание которых возможно при создании сервера аутентификации.
Команда для отображения информации о сервере TACACS+:
Admin@nodename# show users auth-server tacacs <tacacs-server-name>
Примеры команд для создания и редактирования сервера TACACS+:
Admin@nodename# create users auth-server tacacs address 10.10.0.11 name "New TACACS+ server" port 1812 secret 12345 enabled on
Admin@nodename# show users auth-server tacacs "New TACACS+ server"
name                 : New TACACS+ server
enabled              : on
address              : 10.10.0.11
port                 : 1812
single-connection    : off
timeout              : 4
Admin@nodename# set users auth-server tacacs "New TACACS+ server" description "New TACACS+ server description"
Admin@nodename# show users auth-server tacacs "New TACACS+ server"
name                 : New TACACS+ server
description          : New TACACS+ server description
enabled              : on
address              : 10.10.0.11
port                 : 1812
single-connection    : off
timeout              : 4
Для удаления сервера:
Admin@nodename# delete users auth-server tacacs <tacacs-server-name>
Настройка сервера NTLM
Настройка сервера NTLM производится на уровне
users auth-server ntlm
Для создания сервера аутентифификации NTLM используется команда со следующей структурой:
Admin@nodename# create users auth-server ntlm <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя NTLM-сервера.
enabled
Включение/отключение сервера аутентификации.
description
Описание сервера аутентификации.
domain
IP-адрес или доменное имя сервера NLM.
Команда для обновления информации о NTLM-сервере:
Admin@nodename# set users auth-server ntlm <ntlm-server-name> <parameter>
Команда для отображения информации о сервере NTLM:
Admin@nodename# show users auth-server ntlm <ntlm-server-name>
Параметры, которые могут быть обновлены, аналогичны с параметрами команды создания сервера аутентификации.
Примеры команд для создания и редактирования сервера NTLM:
Admin@nodename# create users auth-server ntlm name "New NTLM server" domain 10.10.0.12 enabled on
Admin@nodename# show users auth-server ntlm "New NTLM server"
name           : New NTLM server
enabled        : on
domain         : 10.10.0.12
Admin@nodename# set users auth-server ntlm "New NTLM server" description "New NTLM server description"
Admin@nodename# show users auth-server ntlm "New NTLM server"
name           : New NTLM server
description    : New NTLM server description
enabled        : on
domain         : 10.10.0.12
Для удаления сервера:
Admin@nodename# delete users auth-servers ntlm <ntlm-server-name>
Настройка сервера SAML IDP
Настройка сервера SAML IDP производится на уровне
users auth-server saml-idp
Для создания сервера аутентификации SAML IDP используется следующая команда:
Admin@nodename# create users auth-server saml-idp <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название сервера SAML IDP.
enabled
Включение/отключение сервера аутентификации.
description
Описание сервера аутентификации.
metadata-url
URL на сервере SAML IDP, где можно скачать xml-файл с корректной конфигурацией для сервис-провайдера (клиента) SAML.
certificate
Сертификат, который будет использован в SAML-клиенте.
sso-url
URL, используемая в сервере SAML IDP в качестве единой точки входа. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации.
sso-binding
Метод, используемый для работы с единой точкой входа SSO. Возможны варианты POST и Redirect. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации.
slo-url
URL, используемый в сервере SAML IDP в качестве единой точки выхода. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации.
slo-binding
Метод, используемый для работы с единой точкой выхода SSO. Возможны варианты POST и Redirect. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации.
Команда для обновления информации о сервере SAML IDP:
Admin@nodename# set users auth-server saml-idp <saml-idp-server-name> <parameter>
Параметры, которые могут быть обновлены, аналогичны с параметрами команды создания сервера аутентификации.
Команда для отображения информации о сервере SAML IDP:
Admin@nodename# show users auth-server saml-idp <saml-idp-server-name>
Примеры команд для создания и редактирования сервера SAML IDP:
Admin@nodename# create users auth-server saml-idp name "New SAML IDP server" slo-url http://logout.example.org sso-url http://login.example.o
rg enabled on
Admin@nodename# show users auth-server saml-idp "New SAML IDP server"
name            : New SAML IDP server
enabled         : on
certificate     : Unused
sso-url         : http://login.example.org
sso-binding     : post
slo-url         : http://logout.example.org
slo-binding     : post
Admin@nodename# set users auth-server saml-idp "New SAML IDP server" description "New SAML IDP server description"
Admin@nodename# show users auth-server saml-idp "New SAML IDP server"
name            : New SAML IDP server
description     : New SAML IDP server description
enabled         : on
certificate     : Unused
sso-url         : http://login.example.org
sso-binding     : post
slo-url         : http://logout.example.org
slo-binding     : post
Для удаления сервера:
Admin@nodename# delete users auth-servers saml-idp <saml-idp-server-name>
v8.x
Настройки пользователей
Настройка профилей аутентификации

## Источник

https://docs.usergate.com/nastrojka-serverov-autentifikacii_1706.html
