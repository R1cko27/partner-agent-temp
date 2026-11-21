---
заголовок: Серверы аутентификации управляемой области
url: https://docs.usergate.com/servery-autentifikacii-upravlyaemoj-oblasti_1422.html
источник: портал документации
получено: 2026-11-20 16:33 +0700
продукт: Management Center
версия: 7.x
раздел: Режим администратора управляемой области
id_статьи: 1422
обновлено: 25 Aug, 2025
ревизия: 6
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Режим администратора управляемой области / Серверы аутентификации управляемой области
---

# Серверы аутентификации управляемой области

Содержание:
Documentation:
Серверы аутентификации — это внешние источники учетных записей пользователей для аутентификации в консоли управления области. Работа сервера аутентификации области аналогична работе сервера аутентификации для UGMC, отличие только в месте их использования.
Раздел
Серверы аутентификации
позволяет произвести настройку LDAP-коннектора, серверов RADIUS, TACACS+. Настройка серверов аутентификации производится на уровне
users auth-server
и будет рассмотрена далее в соответствующих разделах.
Настройка LDAP-коннектора
Настройка LDAP-коннектора производится на уровне
users auth-server ldap
Для создания LDAP-коннектора используется команда:
realmadmin/realm@nodename# create users auth-server ldap <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя LDAP-коннектора.
enabled
Включение/отключение сервера аутентификации.
description
Описание LDAP-коннектора.
ssl
Определяет:
— использование SSL-соединения для подключения к LDAP-серверу.
off
— подключение к LDAP-серверу без использования SSL-соединения.
address
IP-адрес контроллера или название домена LDAP.
bind-dn
Имя пользователя, которое будет использоваться для подключения к серверу; указывается в формате DOMAIN\username или username@domain. Пользователь должен быть заведён в домене.
password
Пароль пользователя для подключения к домену.
domains
Список доменов, которые обслуживаются указанным контроллером домена.
search-roots
Список путей в сервере LDAP, начиная с которых система будет осуществлять поиск пользователей и групп. Необходимо указывать полное имя, например, ou=Office,dc=example,dc=com. Если пути поиска не указаны, то поиск производится по всему каталогу, начиная от корня.
Для редактирования информации о существующем LDAP-коннекторе используется команда:
realmadmin/realm@nodename# set users auth-server ldap <ldap-server-name> <parameter>
Параметры, доступные для обновления, аналогичны параметрам создания LDAP-коннектора.
Команда для отображения информации о LDAP-коннекторе:
realmadmin/realm@nodename# show users auth-server ldap <ldap-server-name>
Примеры команд создания и редактирования LDAP-коннектора:
realmadmin/realm@nodename# create users auth-server ldap name "New LDAP connector" ssl on address 10.10.0.10 bind-dn ug@testd.local password 12345 domains [ testd.local ] search-roots [ dc=testd,dc=local ] enabled on
realmadmin/realm@nodename# show users auth-server ldap "New LDAP connector"
name             : New LDAP connector
enabled          : on
ssl              : on
address          : 10.10.0.10
bind-dn          : ug@testd.local
domains          : testd.local
search-roots     : dc=testd,dc=local
keytab_exists    : off
realmadmin/realm@nodename# set users auth-server ldap "New LDAP connector" description "New LDAP connector description"
realmadmin/realm@nodename# show users auth-server ldap "New LDAP connector"
name             : New LDAP connector
description      : New LDAP connector description
enabled          : on
ssl              : on
address          : 10.10.0.10
bind-dn          : ug@testd.local
domains          : testd.local
search-roots     : dc=testd,dc=local
keytab_exists    : off
Для удаления LDAP-коннектора используется команда:
realmadmin/realm@nodename# delete users auth-server ldap <ldap-server-name> <parameter>
Также возможно удаление отдельных параметров LDAP-коннектора. Для удаления доступны следующие параметры:
domains
search-roots
Настройка RADIUS-сервера
Настройка RADIUS-сервера производится на уровне
users auth-server radius
Для создания сервера аутентификации RADIUS используется команда со следующей структурой:
realmadmin/realm@nodename# create users auth-server radius <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя RADIUS-сервера.
enabled
Включение/отключение сервера аутентификации.
description
Описание сервера аутентификации.
secret
Общий ключ, используемый протоколом RADIUS для аутентификации.
addresses
IP-адрес и UDP-порт, на котором сервер RADIUS слушает запросы (по умолчанию порт 1812); указывается в формате <ip:port>.
Команда для обновления информации о сервере RADIUS:
realmadmin/realm@nodename# set users auth-server radius <radius-server-name> <parameter>
Параметры, которые могут быть обновлены, соответствуют параметрам, указание которых возможно при создании сервера аутентификации.
Команда для отображения информации о RADIUS-сервере:
realmadmin/realm@nodename# show users auth-server radius <radius-server-name>
Примеры команд создания и редактирования RADIUS-сервера:
realmadmin/realm@nodename# create users auth-server radius name "New RADIUS server" addresses [ 10.10.0.9:1812 ] secret 12345 enabled on
realmadmin/realm@nodename# show users auth-server radius "New RADIUS server"
name           : New RADIUS server
enabled        : on
addresses      :
host    : 10.10.0.9
port    : 1812
realmadmin/realm@nodename# set users auth-server radius "New RADIUS server" description "New RADIUS server description"
realmadmin/realm@nodename# show users auth-server radius "New RADIUS server"
name           : New RADIUS server
description    : New RADIUS server description
enabled        : on
addresses      :
host    : 10.10.0.9
port    : 1812
Для удаления сервера:
realmadmin/realm@nodename# delete users auth-server radius <radius-server-name> <parameter>
Также возможно удаление отдельных параметров RADIUS-сервера. Для удаления доступны следующие параметры:
addresses
Настройка сервера TACACS+
Настройка сервера TACACS+ производится на уровне
users auth-server tacacs
Для создания сервера аутентификации TACACS+ используется команда со следующей структурой:
realmadmin/realm@nodename# create users auth-server tacacs <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Имя сервера TACACS+.
enabled
Включение/отключение сервера.
description
Описание сервера аутентификации.
secret
Общий ключ, используемый протоколом TACACS+ для аутентификации.
address
IP-адрес сервера TACACS+.
port
UDP-порт, на котором сервер TACACS+ слушает запросы на аутентификацию. По умолчанию это порт UDP 1812.
single-connection
Использовать одно TCP-соединение для работы с сервером TACACS+.
timeout
Время ожидания сервера TACACS+ для получения аутентификации. По умолчанию 4 секунды.
Команда для редактирования информации о сервере TACACS+:
realmadmin/realm@nodename# set users auth-server tacacs <tacacs-server-name> <parameter>
Параметры, которые могут быть обновлены, соответствуют параметрам, указание которых возможно при создании сервера аутентификации.
Команда для отображения информации о сервере TACACS+:
realmadmin/realm@nodename# show users auth-server tacacs <tacacs-server-name>
Примеры команд для создания и редактирования сервера TACACS+:
realmadmin/realm@nodename# create users auth-server tacacs address 10.10.0.11 name "New TACACS+ server" port 1812 secret 12345 enabled on
realmadmin/realm@nodename# show users auth-server tacacs "New TACACS+ server"
name                 : New TACACS+ server
enabled              : on
address              : 10.10.0.11
port                 : 1812
single-connection    : off
timeout              : 4
realmadmin/realm@nodename#set users auth-server tacacs "New TACACS+ server" description "New TACACS+ server description"
realmadmin/realm@nodename# show users auth-server tacacs "New TACACS+ server"
name                 : New TACACS+ server
description          : New TACACS+ server description
enabled              : on
address              : 10.10.0.11
port                 : 1812
single-connection    : off
timeout              : 4
Для удаления сервера:
realmadmin/realm@nodename# delete users auth-server tacacs <tacacs-server-name>
v7.x
Администраторы управляемой области
Профили аутентификации управляемой области

## Источник

https://docs.usergate.com/servery-autentifikacii-upravlyaemoj-oblasti_1422.html
