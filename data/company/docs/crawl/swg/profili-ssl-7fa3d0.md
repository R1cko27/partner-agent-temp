---
заголовок: Профили SSL
url: https://docs.usergate.com/profili-ssl_2617.html
источник: портал документации
получено: 2026-11-20 16:24 +0700
продукт: SWG
версия: 7.5.x
раздел: Профили SSL
id_статьи: 2617
обновлено: 19 Mar, 2026
ревизия: 4
---

# Профили SSL

Профиль SSL позволяет указать протоколы SSL или отдельные алгоритмы шифрования и цифровой подписи, которые в дальнейшем могут быть использованы в правилах инспектирования SSL, в настройках веб-консоли, страницы авторизации, страницы блокировки, веб-портале.
Для создания профиля SSL в разделе
Настройки ➜ Библиотеки ➜ Профили SSL
нажмите
Добавить
и укажите необходимые параметры профиля.
Параметр
Описание
Название
Название профиля SSL
Описание
Описание профиля SSL
Протоколы SSL
Минимальная версия TLS
— устанавливает минимальную версию TLS, которая может быть использована в данном профиле.
Максимальная версия TLS
— устанавливает максимальную версию TLS, которая может быть использована в данном профиле.
Оба эти параметра определяют диапазон версий TLS, которые будут поддерживаться данным профилем
Наборы алгоритмов шифрования
Раздел позволяет выбрать необходимые алгоритмы шифрования и цифровой подписи. Возможные значения указаны в виде строк, в которых перечислены алгоритм и подпись. Администратор может указать только те наборы алгоритмов и подписей, которые считает нужным для безопасной работы организации. Список поддерживаемых комбинаций:
TLS AES 128 CCM SHA256
TLS AES 128 GCM SHA256
TLS AES 256 GCM SHA384
TLS DHE DSS WITH 3DES EDE CBC SHA
TLS DHE DSS WITH AES 128 CBC SHA
TLS DHE DSS WITH AES 128 CBC SHA256
TLS DHE DSS WITH AES 128 GCM SHA256
TLS DHE DSS WITH AES 256 CBC SHA
TLS DHE DSS WITH AES 256 CBC SHA256
TLS DHE DSS WITH AES 256 GCM SHA384
TLS DHE RSA WITH 3DES EDE CBC SHA
TLS DHE RSA WITH AES 128 CBC SHA
TLS DHE RSA WITH AES 128 CBC SHA256
TLS DHE RSA WITH AES 128 GCM SHA256
TLS DHE RSA WITH AES 256 CBC SHA
TLS DHE RSA WITH AES 256 CBC SHA256
TLS DHE RSA WITH AES 256 GCM SHA384
TLS ECDH ECDSA WITH 3DES EDE CBC SHA
TLS ECDH ECDSA WITH AES 128 CBC SHA
TLS ECDH ECDSA WITH AES 128 CBC SHA256
TLS ECDH ECDSA WITH AES 128 GCM SHA256
TLS ECDH ECDSA WITH AES 256 CBC SHA
TLS ECDH ECDSA WITH AES 256 CBC SHA384
TLS ECDH ECDSA WITH AES 256 GCM SHA384
TLS ECDH RSA WITH 3DES EDE CBC SHA
TLS ECDH RSA WITH AES 128 CBC SHA
TLS ECDH RSA WITH AES 128 CBC SHA256
TLS ECDH RSA WITH AES 128 GCM SHA256
TLS ECDH RSA WITH AES 256 CBC SHA
TLS ECDH RSA WITH AES 256 CBC SHA384
TLS ECDH RSA WITH AES 256 GCM SHA384
TLS ECDHE ECDSA WITH 3DES EDE CBC SHA
TLS ECDHE ECDSA WITH AES 128 CBC SHA
TLS ECDHE ECDSA WITH AES 128 CBC SHA256
TLS ECDHE ECDSA WITH AES 128 GCM SHA256
TLS ECDHE ECDSA WITH AES 256 CBC SHA
TLS ECDHE ECDSA WITH AES 256 CBC SHA384
TLS ECDHE ECDSA WITH AES 256 GCM SHA384
TLS ECDHE RSA WITH 3DES EDE CBC SHA
TLS ECDHE RSA WITH AES 128 CBC SHA
TLS ECDHE RSA WITH AES 128 CBC SHA256
TLS ECDHE RSA WITH AES 128 GCM SHA256
TLS ECDHE RSA WITH AES 256 CBC SHA
TLS ECDHE RSA WITH AES 256 CBC SHA384
TLS ECDHE RSA WITH AES 256 GCM SHA384
TLS RSA WITH 3DES EDE CBC SHA
TLS RSA WITH AES 128 CBC SHA
TLS RSA WITH AES 128 CBC SHA256
TLS RSA WITH AES 128 GCM SHA256
TLS RSA WITH AES 256 CBC SHA
TLS RSA WITH AES 256 CBC SHA256
TLS RSA WITH AES 256 GCM SHA384
Установка алгоритмов шифрования для стандартных протоколов
Этот раздел можно использовать для облегчения выбора необходимых алгоритмов шифрования и подписи для стандартных протоколов TLS. Администратор может указать в поле
Выберите протокол для установки алгоритмов
необходимые версии протоколов TLS, нажать на кнопку
Применить
, и алгоритмы, соответствующие выбранной версии протокола автоматически будут отмечены. Можно последовательно добавить несколько версий протокола TLS
По умолчанию в продукте создано несколько профилей SSL, которые могут быть использованы администратором, изменены или удалены при необходимости.
Профиль
Описание
Default SSL profile
Содержит алгоритмы и подписи, соответствующие версиям с TLS v.1.1 до TLS v.1.2. Это наиболее распространенные версии протоколов, используемые в сети интернет в данное время. Данный профиль используется по умолчанию в:
Правилах инспектирования трафика SSL.
Для страницы авторизации Captive-портала.
Для страницы блокировки.
В веб-портале
Default SSL profile (TLSv1.3)
Содержит алгоритмы и подписи, соответствующие версии TLS v.1.3. По умолчанию не используется
Default SSL profile (web console)
Содержит алгоритмы и подписи, соответствующие версиям с TLS v.1.0 до TLS v.1.2. Данный профиль используется по умолчанию для предоставления SSL-доступа в веб-консоль
Важно!
Изменение этого профиля следует производить с осторожностью. Указание алгоритмов, не поддерживаемых вашим браузером, может привести к потере доступа к веб-консоли.
v7.x
Профили LLDP
Профили пересылки SSL

## Источник

https://docs.usergate.com/profili-ssl_2617.html
