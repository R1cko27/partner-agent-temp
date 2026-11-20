---
заголовок: Настройка профилей аутентификации
url: https://docs.usergate.com/nastrojka-profilej-autentifikacii_2672.html
источник: портал документации
получено: 2026-11-20 16:26 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка профилей аутентификации
id_статьи: 2672
обновлено: 17 Mar, 2026
ревизия: 5
---

# Настройка профилей аутентификации

Technology: Identification and Authentication
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
v7.x
Настройка серверов аутентификации
Настройка Captive-профилей

## Источник

https://docs.usergate.com/nastrojka-profilej-autentifikacii_2672.html
