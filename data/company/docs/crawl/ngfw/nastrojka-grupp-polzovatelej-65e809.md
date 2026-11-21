---
заголовок: Настройка групп пользователей
url: https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_806.html
источник: портал документации
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка групп пользователей
id_статьи: 806
обновлено: 26 Mar, 2024
ревизия: 4
---

# Настройка групп пользователей

Documentation:
Настройка групп пользователей производится на уровне
users group
Для добавления новой группы пользователей используется команда:
Admin@nodename# create users group <parameter>
Возможно указать следующие параметры:
Параметр
Описание
name
Название группы пользователей.
description
Описание группы пользователей.
transient
Указать:
— группа для гостевых пользователей.
off
— не является группой для гостевых пользователей.
users
Добавление пользователей в группу.
ldap-users
Добавление пользователей LDAP. При добавлении пользователей LDAP необходимо указать LDAP-коннектор (
ldap-users connector <ldap-server-name> users + [ <domain\user1> <domain\user2> ... ]
Для редактирования информации о группе пользователей необходимо воспользоваться следующей командой (параметры, доступные для обновления, аналогичны с параметрами, доступными при создании группы):
Admin@nodename# set users group <group-name> <parameter>
Для отображения настроек группы используется следующая команда:
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
С использованием следующих команд можно удалить группу пользователей или отдельных пользователей группы:
Admin@nodename# delete users group <group-name>
Для удаления локальных пользователей:
Admin@nodename# delete users group <group-name> users [ <user1> <user2> ... ]
Для удаления пользователей LDAP:
Admin@nodename# delete users group <group-name> ldap-users connector <ldap-server-name> users [ <domain\user1> <domain\user2> ... ]
Пример удаления из группы пользователя LDAP:
Admin@nodename# delete users group "Test user group" ldap-users connector "LDAP connector" users [ testd.local\user1 ]
v7.x
Настройка раздела Пользователи и устройства
Настройки пользователей

## Источник

https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_806.html
