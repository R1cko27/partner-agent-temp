---
заголовок: Профили аутентификации управляемой области
url: https://docs.usergate.com/profili-autentifikacii-upravlyaemoj-oblasti_1423.html
получено: 2026-11-20 16:33 +0700
продукт: Management Center
версия: 7.x
раздел: Режим администратора управляемой области
id_статьи: 1423
обновлено: 25 Aug, 2025
ревизия: 5
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Режим администратора управляемой области / Профили аутентификации управляемой области
---

# Профили аутентификации управляемой области

Documentation:
Профиль позволяет определить набор способов аутентификации пользователей в консоли администрирования UserGate.
Настройка профилей аутентификации производится на уровне
users auth-profile
Для создания профиля аутентификации используется следующая команда:
realmadmin/realm@nodename# create users auth-profile <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля.
description
Описание профиля.
auth-methods
Метод аутентификации:
ldap
: аутентификация с использованием LDAP-коннектора.
radius
: аутентификация с использованием RADIUS-сервера.
tacacs
: аутентификация с использованием сервера TACACS+.
expiration-time
Время жизни авторизованного пользователя; указывается в секундах. Через указанный промежуток времени пользователь перейдёт в статус Unknown user; необходима повторная авторизация пользователя.
idle-time
Время бездействия до отключения; указывается в секундах. Через указанный промежуток времени при отсутствии активности пользователь перейдёт в статус Unknown user.
lockout-time
Время, на которое блокируется учетная запись пользователя при достижении указанного числа неудачных попыток аутентификации; указывается в секундах.
max-attempts
Число неудачных попыток аутентификации до блокировки учётной записи пользователя.
Команда для редактирования настроек профилей аутентификации:
realmadmin/realm@nodename# set users auth-profile <auth-profile-name> <parameter>
Для обновления доступен список параметров, аналогичный списку параметров команды
create
Пример создания и редактирования профиля аутентификации пользователя:
realmadmin/realm@nodename# create users auth-profile name "New LDAP auth profile" auth-methods ldap [ "New LDAP connector" ]
realmadmin/realm@nodename# show users auth-profile "New LDAP auth profile"
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
realmadmin/realm@nodename# set users auth-profile "New LDAP auth profile" description "New LDAP auth profile description"
realmadmin/realm@nodename# show users auth-profile "New LDAP auth profile"
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
Через интерфейс командной строки возможно удаление всего профиля или отдельных способов аутентификации, заданных в профиле. Для этого используются следующие команды.
Для удаления профиля аутентификации:
realmadmin/realm@nodename# delete users auth-profile <auth-profile-name>
Для удаления методов аутентификации, заданных в профиле, необходимо указать метод аутентификации (доступные методы авторизации перечислены в таблице выше):
realmadmin/realm@nodename# delete users auth-profile <auth-profile-name> auth-methods <auth-metod>
v7.x
Серверы аутентификации управляемой области
Каталоги пользователей управляемой области

## Источник

https://docs.usergate.com/profili-autentifikacii-upravlyaemoj-oblasti_1423.html
