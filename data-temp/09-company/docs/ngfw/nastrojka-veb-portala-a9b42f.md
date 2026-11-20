---
заголовок: Настройка веб-портала
url: https://docs.usergate.com/nastrojka-veb-portala_837.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка веб-портала
id_статьи: 837
обновлено: 14 May, 2025
ревизия: 10
---

# Настройка веб-портала

Documentation:
Настройка веб-портала производится на уровне
global-portal web-portal
. О структуре команд подробнее читайте в разделе
UserGate Policy Language
Структура команды создания страницы веб-портала:
Admin@nodename# create global-portal web-portal <position> upl-rule <parameters>
Параметры настройки закладок веб-портала:
Параметр
Описание
Действие для создания правила с помощью UPL.
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название закладки.
Например:
name("Example of bookmark publishing")
desc
Описание закладки.
Например:
desc("Example of bookmark publishing configured in CLI")
url
URL ресурса, который необходимо опубликовать через веб-портал. Необходимо указывать полный URL, начиная с http://, https://, ftp://, ssh:// или rdp://.
URL указывается как
url = "http://www.example.com"
url.domain
При указанном значении домена прямого доступа пользователь может получить доступ к публикуемому ресурсу, минуя веб-портал, подключаясь к указанному домену.
Для указания домена прямого доступа:
url.domain = "example.com"
rdp_check_session_alive
Разрыв сессии RDP по завершению авторизации на веб-портале:
rdp_check_session_alive(yes)
или
rdp_check_session_alive(true)
— разрывать сессию.
rdp_check_session_alive(no)
или
rdp_check_session_alive(false)
— не разрывать сессию.
ssl_profile
Профиль SSL для построения защищенного канала для отображения веб-портала; указывается:
ssl_profile("SSL profile example")
certificate
Сертификат, который будет использоваться для создания HTTPS-соединения. Чтобы задать сертификат:
certificate("Certificate example")
icon
Иконка, которая будет отображаться на веб-портале для данной закладки. Возможно указать одну из предопределенных иконок, указать внешний URL, по которому доступна иконка или загрузить свою иконку.
Можно указать:
icon("Default icon name")
— использовать штатную иконку (в скобках указывается название штатной иконки).
icon("Icon encoded with Base64")
— использовать свою иконку. Необходимо указать содержимое файла, кодированное с использованием Base64.
icon("http://www.icon-url-example.com")
— указать URL для использования сторонней иконки.
additional_url
Вспомогательные URL, необходимые для работы основного URL, но которые нет необходимости публиковать для пользователей. Для указания:
additional_url("http://additional-url-example.com")
user
Пользователи и группы пользователей, которым разрешено отображение закладки на веб-портале и которым разрешен доступ к основному и вспомогательным URL.
Для добавления LDAP групп и пользователей необходим корректно настроенный LDAP-коннектор (о настройке LDAP-коннектора через CLI читайте в разделе
Настройка LDAP-коннектора
Примеры добавления пользователей в правило:
user = known
user = "user"
user = "testd.local\\user1"
user = ("user", "testd.local\\user1")
Для редактирования правила веб-портала используется команда:
Admin@nodename# set global-portal web-portal <position> upl-rule <parameters>
Для просмотра параметров правил веб-портала используется команда:
Admin@nodename# show global-portal web-portal <position>
Пример создания правила веб-портала с использованием UPL:
Admin@nodename# create global-portal web-portal 1 upl-rule OK \
...user = "CN=Default Group,DC=LOCAL" \
...url = "http://www.intranet.loc" \
...name("Test web portal") \
...desc("Test web portal description") \
...enabled(true)
...
Admin@nodename# show global-portal web-portal 1
% ----------------- 1 -----------------
OK \
user = "CN=Default Group,DC=LOCAL" \
url = "http://www.intranet.loc" \
icon("default.svg") \
desc("Test web portal description") \
enabled(true) \
id("2fead5a1-29c3-4835-bbdb-1d0e07f84c28") \
name("Test web portal")
Для удаления правила веб-портала используется команда:
Admin@nodename# delete global-portal web-portal <position>
v7.x
Настройка глобального портала
Настройка правил reverse-прокси

## Источник

https://docs.usergate.com/nastrojka-veb-portala_837.html
