---
заголовок: Профили SSL
url: https://docs.usergate.com/profili-ssl_156.html
источник: портал документации
получено: 2026-11-20 16:13 +0700
продукт: NGFW
версия: 6.1.9, 7.0.1
раздел: Профили SSL
id_статьи: 156
обновлено: 29 Aug, 2024
ревизия: 5
---

# Профили SSL

Documentation:
Профиль SSL позволяет указать протоколы SSL или отдельные алгоритмы шифрования и цифровой подписи, которые в дальнейшем могут быть использованы в правилах инспектирования SSL, в настройках веб-консоли, страницы авторизации, страницы блокировки, веб-портале.
Для создания профиля SSL необходимо нажать на кнопку
Добавить
в разделе
Библиотеки ➜ Профили SSL
и указать необходимые параметры:
Наименование
Описание
Название
Название профиля SSL.
Описание
Описание профиля SSL.
Протоколы SSL
Минимальная версия TLS
— устанавливает минимальную версию TLS, которая может быть использована в данном профиле.
Максимальная версия TLS
— устанавливает максимальную версию TLS, которая может быть использована в данном профиле.
Оба эти параметра определяют диапазон версий TLS, которые будут поддерживаться данным профилем.
Наборы алгоритмов шифрования
Данный раздел позволяет выбрать необходимые алгоритмы шифрования и цифровой подписи. Возможные значения указаны в виде строк, в которых перечислены алгоритм и подпись. Администратор может указать только те наборы алгоритмов и подписей, которые считает нужным для безопасной работы организации. Список поддерживаемых комбинаций следующий:
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
TLS GOST2012256 WITH 28147 CNT IMIT
TLS GOSTR341001 WITH 28147 CNT IMIT
TLS RSA WITH 3DES EDE CBC SHA
TLS RSA WITH AES 128 CBC SHA
TLS RSA WITH AES 128 CBC SHA256
TLS RSA WITH AES 128 GCM SHA256
TLS RSA WITH AES 256 CBC SHA
TLS RSA WITH AES 256 CBC SHA256
TLS RSA WITH AES 256 GCM SHA384
Установка алгоритмов шифрования для стандартных протоколов
Данный раздел можно использовать для облегчения выбора необходимых алгоритмов шифрования и подписи для стандартных протоколов TLS. Администратор может указать в поле
Выберите протокол для установки алгоритмов
необходимые версии протоколов TLS, нажать на кнопку
Применить
, и алгоритмы, соответствующие выбранной версии протокола автоматически будут отмечены. Можно последовательно добавить несколько версий протокола TLS.
По умолчанию в продукте создано несколько профилей SSL, которые могут быть использованы администратором как есть, либо изменены/удалены при необходимости. Созданы следующие профили SSL:
Наименование
Описание
Default SSL profile
Содержит алгоритмы и подписи, соответствующие версиям с TLS v.1.1 до TLS v.1.2. Это наиболее распространенные версии протоколов, используемые в сети интернет в данное время. Данный профиль используется по умолчанию в:
Правилах инспектирования трафика SSL.
Для страницы авторизации Captive-портала.
Для страницы блокировки.
В веб-портале.
Default SSL profile (TLSv1.3)
Содержит алгоритмы и подписи, соответствующие версии TLS v.1.3. По умолчанию не используется.
Default SSL profile (GOST)
Содержит алгоритмы и подписи, соответствующие TLS с ГОСТ-алгоритмами (TLS GOST2012256 with 28147 CNT IMIT и TLS GOSTR341001 with 28147 CNT IMIT). Может быть использован в организациях, где требуется использование данных алгоритмов, например, для веб-портала. Поддержка данных протоколов должна также быть обеспечена со стороны используемых браузеров. По умолчанию не используется.
Default SSL profile (web console)
Содержит алгоритмы и подписи, соответствующие версиям с TLS v.1.0 до TLS v.1.2. Данный профиль используется по умолчанию для предоставления SSL-доступа в веб-консоль.
Важно!
Изменение данного профиля следует производить с осторожностью. Указание алгоритмов, не поддерживаемых вашим браузером, может привести к потере доступа в веб-консоль!
v6.x
v7.x
Также опубликовано в
Документация -> NGFW -> NGFW 7.0.1 Руководство администратора -> Библиотеки элементов
Профили Netflow
Диагностика и мониторинг

## Источник

https://docs.usergate.com/profili-ssl_156.html
