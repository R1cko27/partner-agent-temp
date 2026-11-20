---
заголовок: Настройка раздела Пользователи и устройства
url: https://docs.usergate.com/nastrojka-razdela-pol6zovateli-i-ustrojstva-921/
получено: 2026-11-20 16:33 +0700
продукт: SWG
версия: 7.5
раздел: Интерфейс командной строки
крошки: Главная / Документация / SWG / SWG 7.5.x Руководство администратора / Интерфейс командной строки / Настройка раздела Пользователи и устройства
---

# Настройка раздела Пользователи и устройства

Настройка групп пользователей
Настройки пользователей
Настройка серверов аутентификации
Настройка профилей аутентификации
Настройка Captive-профилей
Captive-портал
Настройка терминальных серверов
Настройка профилей MFA (многофакторной аутентификации)
Просмотр информации об авторизованных пользователях
Настройка применения политик к пользователям
Настройка подключения к серверу регистрации доверенных браузеров
Настройка групп пользователей
Группы пользователей настраиваются на уровне
users group
Для добавления новой группы пользователей используется команда:
Admin@nodename# create users group <parameter>
Далее необходимо указать параметры группы.
Параметр
Описание
name
Название группы пользователей
description
Описание группы пользователей
transient
Указать:
— группа для гостевых пользователей;
off
— не является группой для гостевых пользователей
users
Добавление пользователей в группу.
ldap-users
Добавление пользователей LDAP. При добавлении пользователей LDAP необходимо указать LDAP-коннектор (
ldap-users connector <ldap-server-name> users + [ <domain\user1> <domain\user2> ... ]
Команда для изменения параметров группы пользователей (параметры, доступные для обновления, аналогичны с параметрами, доступными при создании группы):
Admin@nodename# set users group <group-name> <parameter>
Команда для отображения параметров группы:
Admin@nodename# show users group <group-name>
Примеры команд создания и редактирования группы пользователей:
Admin@nodename# create users group name "Test user group" ldap-users connector "LDAP connector" users [ testd.local\user1 ]
Admin@nodename# show users group "Test user group"
name            : Test user group
is-ldap         : off
is-transient    : off
users           : user1 user1 (testd.local\user1)
Admin@nodename# set users group "Test user group" users [ user2 ]
Admin@nodename# show users group "Test user group"
name            : Test user group
is-ldap         : off
is-transient    : off
users           : user2; user1 user1 (testd.local\user1)
Команда для удаления группы пользователей или отдельных пользователей из группы:
Admin@nodename# delete users group <group-name>
Команда для удаления локальных пользователей:
Admin@nodename# delete users group <group-name> users [ <user1> <user2> ... ]
Клманда для удаления пользователей LDAP:
Admin@nodename# delete users group <group-name> ldap-users connector <ldap-server-name> users [ <domain\user1> <domain\user2> ... ]
Пример удаления из группы пользователя LDAP:
Admin@nodename# delete users group "Test user group" ldap-users connector "LDAP connector" users [ testd.local\user1 ]
Просмотреть как статью
к началу
Настройки пользователей
Настройка пользователей выполняется на уровне
users user
Команда для добавления пользователей:
Admin@nodename# create users user <parameter>
Далее необходимо указать параметры пользователей.
Параметр
Описание
enabled
Включение/отключение пользователя
name
Имя пользователя
login
Логин пользователя — для идентификации по имени и паролю. В этом случае потребуется настроить Captive-портал, где пользователь сможет ввести данное имя и пароль для авторизации
password
Пароль пользователя — для идентификации по имени и паролю. В этом случае потребуется настроить Captive-портал, где пользователь сможет ввести данное имя и пароль для авторизации
expiration-date
Срок действия учётной записи пользователя. Указывается в формате YYYY-MM-DD
groups
Группы, в которые будет добавлен пользователь
IP-адреса для идентификации пользователя; пользователь всегда должен получать доступ в сеть с указанных адресов
mac
МАС-адреса для идентификации пользователей; пользователь всегда должен получать доступ в сеть с указанных адресов
ip-range
Диапазон IP-адресов для идентификации пользователя; пользователь всегда должен получать доступ в сеть с адреса из указанного диапазона. Диапазон задаётся в формате:
<IP_start-IP_end
ip-mac
Идентификация пользователя с помощью комбинации MAC и IP-адресов; пользователь всегда должен получать доступ в сеть с указанных адресов. Указывается в формате <
ip-ma
vlan-tag
Тег VLAN ля идентификации пользователя
emails
Почтовые адреса пользователя
phones
Номера телефонов пользователя
Команда для изменения параметров учётной записи пользователя:
Admin@nodename# set users user <user-name> <parameter>
Список доступных параметров аналогичен списку параметров, доступному при создании учётной записи пользователя.
Команда для просмотра учётной записи пользователя:
Admin@nodename# show users user <user-name>
Пример команд создания и редактирования учетной записи пользователя:
Admin@nodename# create users user name user_2 login user2 password 12345 expiration-date 2023-12-31 ip [ 192.168.100.112 ] enabled on
Admin@nodename# show users user user_2
name               : user_2
login              : user2
enabled            : on
expiration-date    : December 31, 2023, 00:00
ip                 : 192.168.100.112
Admin@nodename# set users user user_2 emails [ example@example.org ]
Admin@nodename# show users user user_2
name               : user_2
login              : user2
enabled            : on
emails             : example@example.org
expiration-date    : December 31, 2023, 00:00
ip                 : 192.168.100.112
Команда для удаления учётной записи пользователя:
Admin@nodename# delete users user <user-login>
Также имеется возможность удаления определённой информации из учётной записи. Для удаления доступны (при удалении требуется ввод значения параметра):
groups
static-addresses
emails
phones
Просмотреть как статью
к началу
Настройка серверов аутентификации
Настройка серверов аутентификации выполняется на уровне
users auth-server
С помощью команд этого раздела вы можете выполнить настройку LDAP-коннектора, серверов RADIUS, TACACS+, NTLM, SAML IDP
Настройка LDAP-коннектора
LDAP-коннектор настраивается на уровне
users auth-server ldap
Для создания LDAP-коннектора используется команда:
Admin@nodename# create users auth-server ldap <parameter>
Далее необходимо указать параметры коннектора.
Параметр
Описание
name
Имя LDAP-коннектора
enabled
Включение/отключение сервера аутентификации
description
Описание LDAP-коннектора
ssl
Определяет:
— использование SSL-соединения для подключения к LDAP-серверу;
off
— подключение к LDAP-серверу без использования SSL-соединения
address
IP-адрес контроллера или название домена LDAP
bind-dn
Имя пользователя, которое будет использоваться для подключения к серверу; указывается в формате DOMAIN\username или username
domain. Пользователь должен быть заведён в домене
password
Пароль пользователя для подключения к домену
cache-ttl
Время жизни записей LDAP-кэша. (Опция доступна начиная с релиза UGOS 7.1.3)
domains
Список доменов, которые обслуживаются указанным контроллером домена
search-roots
Список путей в сервере LDAP, начиная с которых система будет осуществлять поиск пользователей и групп. Необходимо указывать полное имя, например, ou=Office,dc=example,dc=com. Если пути поиска не указаны, то поиск производится по всему каталогу, начиная от корня
Команда для редактирования информации о существующем LDAP-коннекторе:
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
Команда для удаления LDAP-коннектора:
Admin@nodename# delete users auth-server ldap <ldap-server-name> <parameter>
Также возможно удаления отдельных параметров LDAP-коннектора. Для удаления доступны следующие параметры:
domains
search-roots
Настройка RADIUS-сервера
Настройка RADIUS-сервера выполняется на уровне
users auth-server radius
Для создания сервера аутентификации RADIUS используется команда:
Admin@nodename# create users auth-server radius <parameter>
Далее необходимо указать параметры сервера.
Параметр
Описание
name
Имя RADIUS-сервера
enabled
Включение или отключение сервера аутентификации
description
Описание сервера аутентификации
secret
Общий ключ, используемый протоколом RADIUS для аутентификации
addresses
IP-адрес и UDP-порт, на котором сервер RADIUS слушает запросы (по умолчанию порт 1812); указывается в формате <
ip:port
Команда для изменения параметров сервера RADIUS:
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
Команда для удаления сервера:
Admin@nodename# delete users auth-server radius <radius-server-name> <parameter>
Также возможно удаления отдельных параметров RADIUS-сервера. Для удаления доступны следующие параметры:
addresses
Настройка сервера TACACS+
Настройка сервера TACACS+ выполняется на уровне users auth-server tacacs.
Для создания сервера аутентификации TACACS+ используется команда:
Admin@nodename# create users auth-server tacacs <parameter>
Далее необходимо указать параметры сервера.
Параметр
Описание
name
Имя сервера TACACS+
enabled
Включение или отключение сервера
description
Описание сервера аутентификации
secret
Общий ключ, используемый протоколом TACACS+ для аутентификации
address
IP-адрес сервера TACACS+
port
UDP-порт, на котором сервер TACACS+ слушает запросы на аутентификацию. По умолчанию это порт UDP 1812
single-connection
Использовать одно TCP-соединение для работы с сервером TACACS+
timeout
Время ожидания сервера TACACS+ для получения аутентификации. По умолчанию 4 секунды
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
Команда для удаления сервера:
Admin@nodename# delete users auth-server tacacs <tacacs-server-name>
Настройка сервера NTLM
Настройка сервера NTLM выполняется на уровне
users auth-server ntlm
Для создания сервера аутентифификации NTLM используется команда:
Admin@nodename# create users auth-server ntlm <parameter>
Далее необходимо указать параметры сервера.
Параметр
Описание
name
Имя NTLM-сервера
enabled
Включение или отключение сервера аутентификации
description
Описание сервера аутентификации
domain
IP-адрес или доменное имя сервера NLM
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
Команда для удаления сервера:
Admin@nodename# delete users auth-servers ntlm <ntlm-server-name>
Настройка сервера SAML IDP
Настройка сервера SAML IDP выполняется на уровне
users auth-server saml-idp
Для создания сервера аутентификации SAML IDP используется команда:
Admin@nodename# create users auth-server saml-idp <parameter>
Далее необходимо указать параметры сервера.
Параметр
Описание
name
Название сервера SAML IDP
enabled
Включение/отключение сервера аутентификации
description
Описание сервера аутентификации
metadata-url
URL на сервере SAML IDP, где можно скачать xml-файл с корректной конфигурацией для сервис-провайдера (клиента) SAML
certificate
Сертификат, который будет использован в SAML-клиенте
sso-url
URL, используемая в сервере SAML IDP в качестве единой точки входа. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации
sso-binding
Метод, используемый для работы с единой точкой входа SSO. Возможны варианты POST и Redirect. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации
slo-url
URL, используемый в сервере SAML IDP в качестве единой точки выхода. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации
slo-binding
Метод, используемый для работы с единой точкой выхода SSO. Возможны варианты POST и Redirect. Смотрите документацию на используемый у вас сервер SAML IDP для более детальной информации
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
Команда для удаления сервера:
Admin@nodename# delete users auth-servers saml-idp <saml-idp-server-name>
Просмотреть как статью
к началу
Настройка профилей аутентификации
Профили аутентификации настраиваются на уровне
users auth-profile
Для создания профиля аутентификации используется команда:
Admin@nodename# create users auth-profile <parameter>
Далее необходимо указать параметры профиля.
Параметр
Описание
name
Название профиля.
description
Описание профиля.
mfa
Указание профиля многофакторной аутентификации (если её необходимо использовать). Для указания профиль MFA должен быть создан заранее. Подробнее о создании профилей MFA с использованием интерфейса командной строки — в разделе «
Настройка профилей MFA (многофакторной аутентификации)
idle-time
Время бездействия до отключения; указывается в секундах. Через указанный промежуток времени при отсутствии активности пользователь перейдёт в статус Unknown user
expiration-time
Время жизни авторизованного пользователя; указывается в секундах. Через указанный промежуток времени пользователь перейдёт в статус Unknown user; необходима повторная авторизация пользователя на Captive-портале
max-attempts
Число неудачных попыток авторизации через Captive-портал до блокировки учётной записи пользователя
lockout-time
Время, на которое блокируется учетная запись пользователя при достижении указанного числа неудачных попыток авторизации; указывается в секундах
auth-methods
Метод аутентификации:
local-user-auth
: аутентификация по базе данных локально заведенных пользователей.
policy-accept
: не требуется аутентификация, но, прежде чем получить доступ в интернет, пользователь должен согласиться с политикой использования сети; применяется совместно с профилем Captive-портала, в котором используется страница авторизации Captive portal policy.
http-basic
: аутентификация с помощью метода HTTP Basic.
ldap
: аутентификация с использованием LDAP-коннектора.
radius
: аутентификация с использованием RADIUS-сервера.
tacacs
: аутентификация с использованием сервера TACACS+.
ntlm
: аутентификация с использованием NTLM-сервера.
saml-idp
: аутентификация с использованием сервера SAML IDP
Команда для изменения параметров профилей аутентификации:
Admin@nodename# set users auth-profile <auth-profile-name> <parameter>
Для обновления доступен список параметров, аналогичный списку параметров команды
create
Пример создания и редактирования профиля аутентификации пользователя:
Admin@nodename# create users auth-profile name "New LDAP auth profile" auth-methods ldap [ "New LDAP connector" ]
Admin@nodename# show users auth-profile "New LDAP auth profile"
name               : New LDAP auth profile
max-attempts       : 5
idle-time          : 900
expiration-time    : 86400
lockout-time       : 300
mfa                : none
auth-methods       :
http-basic         : off
local-user-auth    : off
policy-accept      : off
ldap               : New LDAP connector
Admin@nodename# set users auth-profile "New LDAP auth profile" description "New LDAP auth profile description"
Admin@nodename# show users auth-profile "New LDAP auth profile"
name               : New LDAP auth profile
description        : New LDAP auth profile description
max-attempts       : 5
idle-time          : 900
expiration-time    : 86400
lockout-time       : 300
mfa                : none
auth-methods       :
http-basic         : off
local-user-auth    : off
policy-accept      : off
ldap               : New LDAP connector
Команда для удаления профиля аутентификации:
Admin@nodename# delete users auth-profile <auth-profile-name>
Команда для удаления методов аутентификации, заданных в профиле:
Admin@nodename# delete users auth-profile <auth-profile-name> auth-methods <auth-metod>
Просмотреть как статью
к началу
Настройка Captive-профилей
Captive-профили настраиваются на уровне
users captive-profiles
Для создания Captive-профиля используется команда:
Admin@nodename# create users captive-profiles <parameter>
Далее необходимо указать параметры профиля.
Параметр
Описание
name
Название captive-профиля
description
Описание captive-профиля
auth-template
Шаблон страницы авторизации
auth-mode
Метод идентификации, с помощью которого UserGate запомнит пользователя:
ip — Запоминать IP-адрес. После успешной авторизации пользователя через Captive-портал UserGate запоминает IP-адрес пользователя, и все последующие соединения с этого IP-адреса будут относятся к данному пользователю; устанавливается по умолчанию.
cookie — Запоминать cookie. После успешной авторизации пользователя через Captive-портал UserGate добавляет в браузер пользователя cookie, с помощью которого идентифицирует последующие соединения данного пользователя
auth-profile
Профиль аутентификации, определяющий методы аутентификации. Подробнее о настройке профилей авторизации с использованием CLI смотрите в разделе
Настройка профилей аутентификации
custom-redirect
URL, куда будет перенаправлен пользователь после успешной авторизации с помощью Captive-портала. Если не заполнено, то пользователь переходит на запрошенный им URL
use-cookie
Возможность сохранения авторизации в браузере на указанное время. Для сохранения информации используются cookie.
on;
off
cookie-exptime
Время, на которое будет сохранена аутентификация; задаётся в часах
enable-ldap
Возможность выбора домена AD/LDAP на странице авторизации:
on;
off
use-captcha
Использование CAPTCHA: пользователю будет предложено ввести код, который ему будет показан на странице авторизации Captive-портала:
on;
off
use-https
Использование HTTPS при отображении страницы авторизации Captive-портала. Необходимо иметь корректно настроенный сертификат для SSL Captive-портала.
on;
off
notification-profile
Профиль оповещения, который будет использоваться для отсылки гостевым пользователям информации о созданном пользователе и его пароле. Подробнее о настройке профилей оповещений с использованием CLI — в разделе «
Настройка профилей оповещений
notification-sender
Отправитель сообщения. Указать имя (в случае использования SMPP-профиля) или email (в случае использования SMTP-профиля)
notification-subject
Тема оповещения при использовании оповещений по email
notification-body
Тело письма. В письме можно использовать специальные переменные {login} и {password}, которые будут заменены на имя пользователя и его пароль. Текст оповещения обособляется кавычками (
exp-time
Дата и время, когда учетная запись временного пользователя будет отключена. Указывается в формате
yyyy-mm-ddThh:mm:ssZ
session-ttl
Продолжительность времени с момента первой авторизации временного пользователя, по истечении которого его учетная запись будет отключена; задаётся в часах
password-len
Длина пароля 1 — 15 символов
password-complexity
Сложность пароля:
num: использование только цифр;
alpha_num: использование букв и цифр;
alpha_num_special: использование букв, цифр и специальных символов
ta-groups
Группа для временных пользователей, в которую будут помещены создаваемые пользователи
captive-auth-mode
Выбор метода аутентификации Captive-профиля:
aaa – аутентификация посредством логина/пароля локального пользователя или через AAA-сервер.
pki – аутентификация посредством X.509 сертификатов
uc-profile
Выбор профиля пользовательского сертификата при аутентификации методом pki.
Команда для изменения параметров профиля:
Admin@nodename# set users captive-profiles <captive-profile-name> <parameter>
При обновлении настроек captive-профиля доступны параметры, аналогичные параметрам, доступным при создании профиля.
Команда для отображения настроек captive-профиля:
Admin@nodename# show users captive-profiles <captive-profile-name>
Пример создания и редактирования captive-профиля:
Admin@nodename# create users captive-profiles name "New captive profile" auth-profile "LDAP auth profile" captive-auth-mode aaa enable-ldap on
Admin@nodename# set users captive-profiles "New captive profile" use-https on
Команда для удаления профиля:
Admin@nodename# delete users captive-profiles <captive-profile-name>
Команда для удаление групп для временных пользователей (всегда должна быть указана хотя бы одна группа для временных пользователей):
Admin@nodename# delete users captive-profiles <captive-profile-name> ta-groups
Просмотреть как статью
к началу
Captive-портал
Правила Captive-портала настраиваются с помощью синтаксиса UPL на уровне
users captive-portal
. Подробнее о структуре команд — в разделе «
UserGate Policy Language
Параметры правил captive-портала.
Параметр
Описание
PASS
Действия правила Captive-портала:
– использовать аутентификацию;
PASS
– не использовать аутентификацию
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила captive-портала.
Например:
name("Captive rule example")
desc
Описание правила captive-портала.
Чтобы задать описание правила:
desc("Captive portal rule example set via CLI")
profile
Captive-профиль указывается при использовании аутентификации на captive-портале. Например,
profile("Example Captive profile")
Подробнее о создании и настройке captive-профилей — в разделе «
Настройка Captive-профилей
rule_log
Включение/отключение записи срабатывания в журнал правил:
rule_log(yes)
или
rule_log(true)
rule_log(no)
или
rule_log(false)
Если параметр не указан, функция журналирования отключена
src.zone
Зона источника.
Для указания зоны источника, например, Trusted:
src.zone = Trusted
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
Коды названий стран доступны
по ссылке
dst.zone
Зона назначения трафика.
Для указания зоны назначения, например, Untrusted:
dst.zone = Untrusted
Подробнее о настройке зон с использованием интерфейса командной строки — в разделе «
Зоны
dst.ip
Добавление списков IP-адресов или доменов назначения.
Для указания списка IP-адресов:
dst.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI — в разделе «
Настройка IP-адресов
Для указания списка доменов назначения:
dst.ip = lib.url()
; в скобках необходимо указать название URL-списка, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки — в разделе «
Настройка списков URL
dst.geoip
Указание GeoIP назначения; необходимо указать код страны (например,
dst.geoip = RU
Коды названий стран доступны
по ссылке
category
Списки категорий и категории URL-фильтрации, для которых будет применяться правило. Для URL-фильтрации необходимо иметь соответствующую лицензию.
Для указания списка категорий URL:
category = lib.category()
; в скобках необходимо указать название списка категорий URL.
Подробнее о создании и настройке категорий URL с использованием интерфейса командной строки — в разделе «
Настройка категорий URL
Для указания категории URL:
category = "URL category name"
url
Списки URL, для которых будет применяться правило.
Для указания списка URL:
url = lib.url()
; в скобках необходимо указать название списка URL
time
Настройка расписания работы правила.
Для установки расписания:
time = lib.time()
; в скобках необходимо указать название группы календарей. Подробнее о настройке календарей — в разделе «
Настройка календарей
Пример создания и редактирования правила captive-портала с использованием UPL:
Admin@nodename# create users captive-portal 1 upl-rule OK \
...profile("New captive profile") \
...rule_log(true) \
...name("Captive portal rule new") \
...
Admin@nodename# show users captive-portal 1
% ----------------- 1 -----------------
OK \
rule_log(yes) \
profile("New captive profile") \
enabled(false) \
id("676df2b1-03e9-42b2-8375-0b8f78c4c47c") \
name("Captive portal rule new")
Admin@nodename# set users captive-portal 1 upl-rule OK \
...src.zone = Trusted \
...dst.zone = Untrusted
...
Admin@nodename# show users captive-portal 1
% ----------------- 1 -----------------
OK \
src.zone = Trusted \
dst.zone = Untrusted \
rule_log(yes) \
profile("New captive profile") \
enabled(false) \
id("676df2b1-03e9-42b2-8375-0b8f78c4c47c") \
name("Captive portal rule new")
Просмотреть как статью
к началу
Настройка терминальных серверов
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
Просмотреть как статью
к началу
Настройка профилей MFA (многофакторной аутентификации)
Профили MFA настраиваются на уровне
users mfa-profiles
Вы можете создать несколько типов профилей:
MFA через TOTP: использование токена TOTP (Time-based One Time Password) в качестве второго фактора аутентификации.
MFA через email: использование одноразового пароля, полученного по email, в качестве второго фактора аутентификации.
MFA через SMS: использование одноразового пароля, полученного по SMS, в качестве второго фактора аутентификации.
Для создания профиля многофакторной аутентификации используется команда:
Admin@nodename# create users mfa-profiles <parameter>
Команда для удаления профиля многофакторной аутентификации:
Admin@nodename# delete users mfa-profiles <mfa-name>
Команда для отображения информации о всех профилях или об определённом профиле MFA:
Admin@nodename# show users mfa-profiles
Admin@nodename# show users mfa-profiles <mfa-name>
Настройка MFA через TOTP
Команда для добавления нового профиля многофакторной аутентификации через TOTP:
Admin@nodename# create users mfa-profiles totp <parameter>
Далее необходимо указать параметры профиля.
Параметр
Описание
name
Название профиля MFA
description
Описание профиля MFA
show-qr-code
QR-код на странице Captive-портала или в электронном письме для облегчения настройки устройства или ПО TOTP-клиента
notification-profile
Выбор профиля оповещения
notification-sender
Отправитель сообщения. Указать имя (в случае использования SMPP-профиля) или email (в случае использования SMTP-профиля)
notification-subject
Тема оповещения при использовании оповещений по email
notification-body
Тело письма. В письме можно использовать специальную переменную
{2fa_auth_code}
, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками (
Команда для редактирования параметров профиля многофакторной аутентификации через TOTP:
Admin@nodename# set users mfa-profiles totp <mfa-totp-name> <parameter>
Параметры, доступные для редактирования, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля многофакторной аутентификации через TOTP:
Admin@nodename# create users mfa-profiles totp name "Test TOTP MFA profile" notification-profile pass show-qr-code on
Admin@nodename# show users mfa-profiles totp "Test TOTP MFA profile"
name                    : Test TOTP MFA profile
show-qr-code            : on
notification-profile    : pass
notification-body       : Your authentication code is {2fa_auth_code}! Do not share it with anybody!
Admin@nodename# set users mfa-profiles totp "Test TOTP MFA profile" description "Test TOTP MFA profile description"
Admin@nodename# show users mfa-profiles totp "Test TOTP MFA profile"
name                    : Test TOTP MFA profile
description             : Test TOTP MFA profile description
show-qr-code            : on
notification-profile    : pass
notification-body       : Your authentication code is {2fa_auth_code}! Do not share it with anybody!
Настройка MFA через email
Команда для добавления нового профиля многофакторной аутентификации через email:
Admin@nodename# create users mfa-profiles smtp <parameter>
Далее необходимо указать параметры профиля.
Параметр
Описание
name
Название профиля MFA
description
Описание профиля MFA
notification-profile
Выбор профиля оповещения
notification-sender
Email отправителя сообщения
notification-subject
Тема оповещения
notification-body
Тело письма. В письме можно использовать специальную переменную
{2fa_auth_code}
, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками (
code-lifetime
Срок действия одноразового пароля; указывается в секундах
Команда для редактирования параметров профиля многофакторной аутентификации через email:
Admin@nodename# set users mfa-profiles smtp <mfa-email-profile> <parameter>
Параметры, доступные для обновления, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля многофакторной аутентификации через email:
Admin@nodename# create users mfa-profiles smtp name "Test SMTP MFA profile" notification-profile "Example SMTP profile" notification-sender sender@example.org notification-subject "Test notification subj" notification-body "Test notification text"
Admin@nodename# show users mfa-profiles smtp "Test SMTP MFA profile"
name                    : Test SMTP MFA profile
notification-profile    : Example SMTP profile
notification-sender     : sender@example.org
notification-subject    : Test notification subj
notification-body       : Test notification text
code-lifetime           : 60
Admin@nodename# set users mfa-profiles smtp "Test SMTP MFA profile" code-lifetime 70
Admin@nodename# show users mfa-profiles smtp "Test SMTP MFA profile"
name                    : Test SMTP MFA profile
notification-profile    : Example SMTP profile
notification-sender     : sender@example.org
notification-subject    : Test notification subj
notification-body       : Test notification text
code-lifetime           : 70
Настройка MFA через SMS
Команда для добавления нового профиля многофакторной аутентификации через SMS:
Admin@nodename# create users mfa-profiles smpp <parameter>
Далее необходимо указать параметры профиля.
Параметр
Описание
name
Название профиля MFA
description
Описание профиля MFA
notification-sender
Имя отправителя сообщения
notification-body
Тело письма. В письме можно использовать специальную переменную
{2fa_auth_code}
, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками (
code-lifetime
Срок действия одноразового пароля; указывается в секундах.
Команда для редактирования параметров профиля многофакторной аутентификации через SMS:
Admin@nodename# set users mfa-profiles smpp <mfa-sms-profile> <parameter>
Параметры, доступные для обновления, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля многофакторной аутентификации через SMS:
Admin@nodename# create users mfa-profiles smpp name "Test SMPP MFA profile" notification-profile "Example SMPP profile" notification-sender Tes_sender notification-body "Test notification text"
Admin@nodename# show users mfa-profiles smpp "Test SMPP MFA profile"
name                    : Test SMPP MFA profile
notification-profile    : Example SMPP profile
notification-sender     : Tes_sender
notification-body       : Test notification text
code-lifetime           : 60
Admin@nodename# set users mfa-profiles smpp "Test SMPP MFA profile" code-lifetime 80
Admin@nodename# show users mfa-profiles smpp "Test SMPP MFA profile"
name                    : Test SMPP MFA profile
notification-profile    : Example SMPP profile
notification-sender     : Tes_sender
notification-body       : Test notification text
code-lifetime           : 80
Просмотреть как статью
к началу
Просмотр информации об авторизованных пользователях
Для просмотра информации об авторизованных пользователях используется команда:
Admin@nodename> show user-auth
Для просмотра деталей аутентификационной сессии определенного пользователя используется команда:
Admin@nodename> show user-auth <user name>
Для удаления сессии определенного пользователя используется команда:
Admin@nodename> clear user-auth <parameter>
В качестве параметра может использоваться как имя пользователя, так и его IP-адрес.
Просмотреть как статью
к началу
Настройка применения политик к пользователям
Для локальных пользователей устройства UserGate политики применяются автоматически.
Если пользователи проходят аутентификацию через LDAP-коннектор, NTLM или Kerberos, то для применения политик к пользователям (в случаях добавления новой LDAP-группы или пользователя в группу, создания правила и применения его к группе LDAP) необходимо сбросить сессии всех пользователей и произвести очистку кэш-памяти LDAP-записей на устройстве UserGate.
С помощью интерфейса командной строки CLI можно сбросить сессии отдельных пользователей. Команда выполняется в режиме конфигурации (configure), для выполнения команды необходимо знать IP-адрес пользователя:
Admin@nodename# execute termination user-sessions ip <IP-address>
Для очистки кэш-памяти используется команда:
Admin@nodename# execute cache ldap-clear
Просмотреть как статью
к началу
Настройка подключения к серверу регистрации доверенных браузеров
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
Просмотреть как статью
к началу

## Источник

https://docs.usergate.com/nastrojka-razdela-pol6zovateli-i-ustrojstva-921/
