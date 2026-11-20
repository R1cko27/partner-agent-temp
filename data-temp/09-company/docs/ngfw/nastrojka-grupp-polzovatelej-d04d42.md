---
заголовок: Настройка групп пользователей
url: https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_218.html
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 7.0.1
раздел: Настройка групп пользователей
id_статьи: 218
обновлено: 22 Jan, 2024
ревизия: 4
---

# Настройка групп пользователей

Documentation:
Настройка групп пользователей производится на уровне
users group
Для добавления новой группы пользователей используется команда:
Admin@UGOS# create users group
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
ldap-users connector <ldap-server-name> users + [ <domain\user1> domain\user2> ... ]
Для обновления информации о группе пользователей необходимо воспользоваться следующей командой (параметры, доступные для обновления, аналогичны с параметрами, доступными при создании группы):
Admin@UGOS# set users group <group-name>
С использованием следующих команд можно удалить группу пользователей или отдельных пользователей группы:
Admin@UGOS# delete users group <group-name>
Для удаления локальных пользователей:
Admin@UGOS# delete users group <group-name> users [ <user1> <user2> ... ]
Для удаления пользователей LDAP:
Admin@UGOS# delete users group <group-name> ldap-users connector <ldap-server-name> users [ <domain\user1> <domain\user2> ... ]
Для отображения настроек группы используется следующая команда:
Admin@UGOS# show users group <group-name>
v7.x
Настройка раздела Пользователи и устройства
Настройки пользователей

## Источник

https://docs.usergate.com/nastrojka-grupp-pol6zovatelej_218.html
