---
заголовок: Настройка управления доступом к консоли NGFW
url: https://docs.usergate.com/nastrojka-upravleniya-dostupom-k-konsoli-usergate_205.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.0.1
раздел: Настройка управления доступом к консоли NGFW
id_статьи: 205
обновлено: 19 Jan, 2024
ревизия: 6
---

# Настройка управления доступом к консоли NGFW

Содержание:
Documentation:
Настройка данного раздела производится на уровне
settings administrators
. В данном разделе описаны настройка параметров защиты учётных записей, настройка администраторов и их профилей.
Общие настройки доступа
Данный раздел позволяет настроить дополнительные параметры защиты учётных записей администраторов. Настройка производится на уровне
settings administrators general
Для изменения параметров необходимо использовать следующую команду
Admin@UGOS# set settings administrators general
Далее необходимо указать параметры, которые необходимо изменить:
Параметр
Описание
password
Изменить пароля текущего администратора.
unblock
Разблокировать администратора.
strong-password
Использовать сложный пароль:
off
num-auth-attempts
Установить максимальное количество неверных попыток аутентификации.
block-time
Указать время блокировки учётной записи в случае достижения администратором максимального количества попыток аутентификации; указывается в секундах (максимальное значение: 3600 секунд).
min-length
Определить минимальную длину пароля (максимальное значение: 100 символов).
min-uppercase
Определить минимальное количество символов в верхнем регистре (максимальное значение: 100 символов).
min-lowercase
Определить минимальное количество символов в нижнем регистре (максимальное значение: 100 символов).
min-digits
Определить минимальное количество цифр (максимальное значение: 100 символов).
min-special-characters
Определить минимальное количество специальных символов (максимальное значение: 100 символов).
max-characters-repetition
Указать максимальную длину блока из одного и того же символа (максимальное значение: 100 символов).
Для просмотра текущих параметров защиты учётных записей администраторов используйте команду:
Admin@UGOS# show settings administrators general
Настройка учётных записей администраторов
Настройка учётных записей администраторов производится на уровне
settings administrators administrators
Для создания учётной записи администратора используется следующая команда:
Admin@UGOS# create settings administrators administrators
Далее необходимо указать тип учётной записи администратора (локальный, пользователь LDAP, группа LDAP, с профилем аутентификации) и указать соответствующие параметры:
Параметр
Описание
local
Добавить локального администратора:
enabled
: включение/отключение учётной записи администратора:
off
login
: логин администратора.
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
password
: пароль администратора.
ldap-user
Добавить пользователя из существующего домена (необходим корректно настроенный LDAP-коннектор; подробнее читайте в разделе
Настройка LDAP-коннектора
enabled
: включение/отключение учётной записи администратора:
off
ldap-login
: логин администратора. Структура команды при указании данного параметра:
Admin@UGOS# create settings administrators administrators ldap-user ... ldap-login connector <ldap-connector-name> user <domain\user> ...
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
ldap-group
Добавить группу пользователей из существующего домена (необходим корректно настроенный LDAP-коннектор; подробнее читайте в разделе
Настройка LDAP-коннектора
enabled
: включение/отключение учётной записи администратора:
off
ldap-login
: логин администратора. Структура команды при указании данного параметра:
Admin@UGOS# create settings administrators administrators ldap-group ... ldap-login connector <ldap-connector-name> group <domain\group> ...
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
admin-auth-profile
Добавить администратора с профилем аутентификации (необходимы корректно настроенные серверы аутентификации; подробнее читайте в разделе
Настройка серверов аутентификации
enabled
: включение/отключение учётной записи администратора:
off
login
: логин администратора.
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
auth-profile
: выбор профиля аутентификации из созданных ранее; подробнее о профилях аутентификации читайте в разделе
Настройка профилей аутентификации
Следующая команда используется для обновления профиля (параметры аналогичны параметрам создания профиля администратора):
Admin@UGOS# set settings administrators administrators <admin-type> <admin-login>
Для удаления учётной записи используется команда:
Admin@UGOS# delete settings administrators administrators <admin-type> <admin-login>
Для отображения информации о всех учётных записях администраторов:
Admin@UGOS# show settings administrators administrators
Для отображения информации об определённой учётной записи администратора:
Admin@UGOS# show settings administrators administrators <admin-type> <admin-login>
Настройка прав доступа профилей администраторов
Настройка прав доступа профилей администраторов производится на уровне
settings administrators admin-profiles
Для создания профиля администратора предназначена следующая команда:
Admin@UGOS# create settings administrators admin-profiles
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля администратора.
description
Описание профиля администратора.
api-permissions
Права доступа к API:
no-access
: нет доступа.
read
: только чтение.
readwrite
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@UGOS# create settings administrators admin-profiles ... api-permissions <permission> all
или
Admin@UGOS# create settings administrators admin-profiles ... api-permissions <permission> [ object ... ]
webui-permissions
Права доступа к веб-интерфейсу UserGate:
no-access
: нет доступа.
read
: только чтение.
readwrite
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@UGOS# create settings administrators admin-profiles ... webui-permissions <permission> all
или
Admin@UGOS# create settings administrators admin-profiles ... webui-permissions <permission> [ object ... ]
cli-permissions
Права доступа к интерфейсу командной строки (CLI):
no-access
: нет доступа.
read
: только чтение.
readwrite
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@UGOS# create settings administrators admin-profiles ... cli-permissions <permission> all
или
Admin@UGOS# create settings administrators admin-profiles ... cli-permissions <permission> [ object ... ]
Следующая команда используется для обновления профиля (параметры аналогичны параметрам создания профиля администратора):
Admin@UGOS# set settings administrators admin-profiles <profile-name>
Чтобы удалить профиль администратора:
Admin@UGOS# delete settings administrators admin-profiles <profile-name>
Для просмотра информации о всех профиля администраторов:
Admin@UGOS# show settings administrators admin-profiles
Для отображения информации об определённом профиле:
Admin@UGOS# show settings administrators admin-profiles <profile-name>
Настройка сессий администраторов
С использованием следующих команд возможен просмотр сессий администраторов, прошедших авторизацию в веб-консоли или CLI, и закрытие сессий (уровень:
settings administrators sessions
Просмотр сессий администраторов текущего узла UserGate (возможен просмотр сессии отдельного администратора: необходимо из предложенного списка выбрать IP-адрес, с которого была произведена авторизация):
Admin@UGOS# show settings administrators sessions
Для отображения сессий доступно использование фильтра:
: IP-адрес, с которого авторизован администратор.
source
: где была произведена авторизация: CLI (
cli
), веб-консоль (
web
) или подключение по SSH (
ssh
admin-login
: имя администратора.
node
: узел кластера UserGate.
Admin@UGOS# show settings administrators sessions ( node <node-name> ip <session-ip> source <cli | web | ssh> admin-login <administrator-login> )
Команда для закрытия сессии администратора; необходимо из предложенного списка выбрать IP-адрес, с которого была произведена авторизация:
Admin@UGOS# execute terminate settings administrators sessions
При закрытии сессии администраторов возможно использование фильтра ( <filter> ). Параметры фильтрации аналогичны параметрам команды
show
Admin@UGOS# execute terminate settings administrators sessions ( node <node-name> ip <session-ip> source <cli | web | ssh> admin-login <administrator-login> )
v7.x
Настройка кластеров
Настройка сертификатов

## Источник

https://docs.usergate.com/nastrojka-upravleniya-dostupom-k-konsoli-usergate_205.html
