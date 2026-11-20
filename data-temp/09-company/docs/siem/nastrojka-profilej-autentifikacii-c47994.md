---
заголовок: Настройка профилей аутентификации
url: https://docs.usergate.com/nastrojka-profilej-autentifikacii_1455.html
получено: 2026-11-20 16:33 +0700
продукт: SIEM
версия: 7.1.x
раздел: Настройка устройства
id_статьи: 1455
обновлено: 25 Mar, 2024
ревизия: 1
крошки: Главная / Документация / SIEM / UserGate SIEM 7.2.x Руководство администратора / Интерфейс командной строки (CLI) / Настройка устройства / Настройка профилей аутентификации
---

# Настройка профилей аутентификации

Documentation:
Technology: Identification and Authentication
Настройка профилей аутентификации производится на уровне
users auth-profile
Для создания профиля аутентификации используется следующая команда:
Admi@nodename# create users auth-profile <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля
description
Описание профиля.
idle-time
Время бездействия до отключения; указывается в секундах. Через указанный промежуток времени при отсутствии активности пользователь перейдёт в статус Unknown user.
expiration-time
Время жизни аутентифицированного пользователя; указывается в секундах. Через указанный промежуток времени пользователь перейдёт в статус Unknown user; необходима повторная аутентификация пользователя.
max-attempts
Число неудачных попыток аутентификации до блокировки учётной записи пользователя.
lockout-time
Время, на которое блокируется учетная запись пользователя при достижении указанного числа неудачных попыток аутентификации; указывается в секундах.
auth-methods
Метод аутентификации:
ldap
: аутентификация с использованием LDAP-коннектора.
radius
: аутентификация с использованием RADIUS-сервера.
tacacs
: аутентификация с использованием сервера TACACS+.
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
Роли пользователей

## Источник

https://docs.usergate.com/nastrojka-profilej-autentifikacii_1455.html
