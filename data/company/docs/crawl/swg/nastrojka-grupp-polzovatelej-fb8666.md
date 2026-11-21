---
заголовок: Настройка групп пользователей
url: https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_2669.html
источник: портал документации
получено: 2026-11-20 16:26 +0700
продукт: SWG
версия: 7.5.x
раздел: Настройка групп пользователей
id_статьи: 2669
обновлено: 17 Mar, 2026
ревизия: 4
---

# Настройка групп пользователей

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
v7.x
Настройка раздела Пользователи и устройства
Настройки пользователей

## Источник

https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_2669.html
