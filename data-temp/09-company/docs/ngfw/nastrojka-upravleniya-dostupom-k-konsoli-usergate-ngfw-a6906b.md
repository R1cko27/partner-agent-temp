---
заголовок: Настройка управления доступом к консоли UserGate NGFW
url: https://docs.usergate.com/nastrojka-upravleniya-dostupom-k-konsoli-usergate-ngfw_794.html
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка управления доступом к консоли UserGate NGFW
id_статьи: 794
обновлено: 26 Mar, 2024
ревизия: 9
---

# Настройка управления доступом к консоли UserGate NGFW

Содержание:
Documentation:
Настройка данного раздела производится на уровне
settings administrators
. В разделе описаны настройка параметров защиты учётных записей, настройка администраторов и их профилей.
Общие настройки доступа
Данный раздел позволяет настроить дополнительные параметры защиты учётных записей администраторов. Настройка производится на уровне
settings administrators general
Для изменения параметров используется следующая команда:
Admin@nodename# set settings administrators general
Параметры, доступные для редактирования:
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
spec-characters
Определить минимальное количество специальных символов (максимальное значение: 100 символов).
char-repetition
Указать максимальную длину блока из одного и того же символа (максимальное значение: 100 символов).
Пример редактирования параметров учетных записей:
Admin@nodename# set settings administrators general block-time 400
Для просмотра текущих параметров защиты учётных записей администраторов используется следующая команда:
Admin@nodename# show settings administrators general
strong-password      : off
block-time           : 400
min-length           : 7
min-uppercase        : 1
min-lowercase        : 1
min-digits           : 1
spec-characters      : 1
char-repetition      : 2
num-auth-attempts    : 10
Настройка учётных записей администраторов
Настройка учётных записей администраторов производится на уровне
settings administrators administrators
Для создания учётной записи администратора используется следующая команда:
Admin@nodename# create settings administrators administrators
Далее необходимо указать тип учётной записи администратора (локальный, пользователь LDAP, группа LDAP, с профилем аутентификации) и установить соответствующие параметры:
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
login
: логин администратора в формате
domain\user
. Структура команды при указании данного параметра:
connector
: название сконфигурированного ранее LDAP-коннектора.
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
Admin@nodename# create settings administrators administrators ldap-user admin-profile "test profile 1" connector "LDAP connector" description "Admin as domain user" login testd.local\user1 enabled on
ldap-group
Добавить группу пользователей из существующего домена (необходим корректно настроенный LDAP-коннектор; подробнее читайте в разделе
Настройка LDAP-коннектора
enabled
: включение/отключение учётной записи администратора:
off
login
: логин администратора
connector
: название используемого LDAP-коннектора.
description
: описание учётной записи администратора.
admin-profile
: профиль администратора. Создание профилей администраторов рассмотрено далее.
Admin@nodename# create settings administrators administrators ldap-group admin-profile "test profile 1" connector "LDAP connector" description "Domain admin group" login testd.local\users enabled on
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
Для редактирования параметров профиля используется команда:
Admin@nodename# set settings administrators administrators <admin-type> <admin-login>
Параметры для редактирования аналогичны параметрам создания профиля администратора.
Для отображения информации о всех учётных записях администраторов:
Admin@nodename# show settings administrators administrators
Для отображения информации об определённой учётной записи администратора:
Admin@nodename# show settings administrators administrators <admin-type> <admin-login>
Пример выполнения команды:
Admin@nodename# show settings administrators administrators ldap-user testd.local\user1
login            : testd.local\user1
enabled          : on
type             : ldap_user
locked           : off
admin-profile    : test profile 1
Для удаления учётной записи используется команда:
Admin@nodename# delete settings administrators administrators <admin-type> <admin-login>
Пример команды:
Admin@nodename# delete settings administrators administrators ldap-user testd.local\user1
Настройка прав доступа профилей администраторов
Настройка прав доступа профилей администраторов производится на уровне
settings administrators profiles
Для создания профиля администратора используется следующая команда:
Admin@nodename# create settings administrators profiles
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
write
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@nodename# create settings administrators profiles ... api-permissions <permission> all
или
Admin@nodename# create settings administrators profiles ... api-permissions <permission> [ object ... ]
webui-permissions
Права доступа к веб-интерфейсу UserGate:
no-access
: нет доступа.
read
: только чтение.
write
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@nodename# create settings administrators profiles ... webui-permissions <permission> all
или
Admin@nodename# create settings administrators profiles ... webui-permissions <permission> [ object ... ]
cli-permissions
Права доступа к интерфейсу командной строки (CLI):
no-access
: нет доступа.
read
: только чтение.
write
: чтение и запись.
Возможно назначение прав сразу на все или на отдельные объекты:
Admin@nodename# create settings administrators profiles ... cli-permissions <permission> all
или
Admin@nodename# create settings administrators profiles ... cli-permissions <permission> [ object ... ]
Для редактирования профиля используется команда:
Admin@nodename# set settings administrators profiles <profile-name> <parameter>
Параметры для редактирования аналогичны параметрам создания профиля администратора.
Для просмотра информации о всех профилях администраторов:
Admin@nodename# show settings administrators profiles
Для отображения информации об определённом профиле:
Admin@nodename# show settings administrators profiles <profile-name>
Чтобы удалить профиль администратора:
Admin@nodename# delete settings administrators profiles <profile-name>
Управление сессиями администраторов
С использованием следующих команд возможен просмотр активных сессий администраторов, прошедших авторизацию в веб-консоли или CLI, и закрытие сессий (уровень:
settings administrators admin-sessions
Просмотр сессий администраторов текущего узла UserGate (возможен просмотр сессии отдельного администратора: необходимо из предложенного списка выбрать IP-адрес, с которого была произведена авторизация):
Admin@nodename# show settings administrators admin-sessions
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
Admin@nodename# show settings administrators admin-sessions ( node <node-name> ip <session-ip> source <cli | web | ssh> admin-login <administrator-login> )
Команда для закрытия сессии администратора; необходимо из предложенного списка выбрать IP-адрес, с которого была произведена авторизация:
Admin@nodename# execute termination admin-sessions <IP-address/connection type>
Пример выполнения команд:
Admin@nodename# show settings administrators admin-sessions
admin-login           : Admin
source                : ssh
session_start_date    : 2023-08-10T11:33:47Z
ip                    : 127.0.0.1
node                  : utmcore@dineanoulwer
admin-login           : Admin
source                : web
session_start_date    : 2023-08-10T11:33:10Z
ip                    : 10.0.2.2
node                  : utmcore@dineanoulwer
Admin@nodename# execute termination admin-sessions 10.0.2.2/web
Admin@nodename# show settings administrators admin-sessions
admin-login           : Admin
source                : ssh
session_start_date    : 2023-08-10T11:33:47Z
ip                    : 127.0.0.1
node                  : utmcore@dineanoulwer
При закрытии сессии администраторов возможно использование фильтра ( <filter> ). Параметры фильтрации аналогичны параметрам команды
show
Admin@nodename# execute termination admin-sessions ( node <node-name> ip <session-ip> source <cli | web | ssh> admin-login <administrator-login> )
v7.x
Настройка кластеров (версия 7.5.0 и выше)
Настройка сертификатов

## Источник

https://docs.usergate.com/nastrojka-upravleniya-dostupom-k-konsoli-usergate-ngfw_794.html
