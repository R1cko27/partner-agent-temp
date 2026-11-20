---
заголовок: Настройка профилей аутентификации
url: https://docs.usergate.com/nastrojka-profilej-autentifikacii_3006.html
получено: 2026-11-20 16:26 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка профилей аутентификации
id_статьи: 3006
обновлено: 06 Apr, 2026
ревизия: 1
---

# Настройка профилей аутентификации

Technology: Identification and Authentication
Настройка профилей аутентификации производится на уровне
users auth-profile
Для создания профиля аутентификации используется следующая команда:
Admin@nodename# create users auth-profile <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля MFA.
description
Описание профиля MFA.
idle-time
Время бездействия до отключения; указывается в секундах. Через указанный промежуток времени при отсутствии активности пользователь перейдёт в статус Unknown user.
expiration-time
Время жизни авторизованного пользователя; указывается в секундах. Через указанный промежуток времени пользователь перейдёт в статус Unknown user; необходима повторная авторизация пользователя на Captive-портале.
max-attempts
Число неудачных попыток авторизации через Captive-портал до блокировки учётной записи пользователя.
lockout-time
Время, на которое блокируется учетная запись пользователя при достижении указанного числа неудачных попыток авторизации; указывается в секундах.
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
ntlm
: аутентификация с использованием NTLM-сервера.
saml-idp
: аутентификация с использованием сервера SAML IDP.
Команда для редактирования настроек профилей аутентификации:
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
Через интерфейс командной строки возможно удаления всего профиля или отдельных способов аутентификации, заданных в профиле. Для этого используются следующие команды.
Для удаления профиля аутентификации:
Admin@nodename# delete users auth-profile <auth-profile-name>
Для удаления методов аутентификации, заданных в профиле, необходимо указать метод аутентификации (доступные методы авторизации перечислены в таблице выше):
Admin@nodename# delete users auth-profile <auth-profile-name> auth-methods <auth-metod>
v7.x
Настройка серверов аутентификации
Настройки сети

## Источник

https://docs.usergate.com/nastrojka-profilej-autentifikacii_3006.html
