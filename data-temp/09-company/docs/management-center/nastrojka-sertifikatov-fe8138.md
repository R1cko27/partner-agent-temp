---
заголовок: Настройка сертификатов
url: https://docs.usergate.com/nastrojka-sertifikatov_1403.html
получено: 2026-11-20 16:32 +0700
продукт: Management Center
версия: 7.x
раздел: Настройка устройства
id_статьи: 1403
обновлено: 21 Mar, 2024
ревизия: 6
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Настройка устройства / Настройка сертификатов
---

# Настройка сертификатов

Documentation:
Раздел
Сертификаты
находится на уровне
settings certificates
Для импорта сертификатов предназначена команда:
Admin/system@nodename# import settings certificates
Далее необходимо указать параметры:
Параметр
Описание
name
Название сертификата, которое будет отображено в списке.
description
Описание сертификата.
certificate-data
Сертификат в формате PEM.
certificate-chain
Цепочка сертификатов в формате PEM.
private-key
Приватный ключ в формате PEM.
passphrase
Пароль для приватного ключа или контейнера PKCS12 (необязательное значение).
Для экспорта доступны сертификаты, вся цепочка сертификатов:
Admin/system@nodename# export settings certificates <certificate-name>
Admin/system@nodename# export settings certificates <certificate-name> with-chain on
С использованием командной строки возможно создание сертификата и CSR:
Admin/system@nodename# create settings certificates type <certificate | csr>
Далее необходимо указание следующих параметров:
Параметр
Описание
name
Название сертификата.
description
Описание сертификата.
country
Страна, в которой выписывается сертификат.
state
Область/штат, в котором выписывается сертификат.
locality
Город, в котором выписывается сертификат.
organization
Название организации, для которой выписывается сертификат.
common-name
Имя сертификата. Рекомендуется использовать только символы латинского алфавита для совместимости с большинством браузеров.
email
Email компании.
Команда для управления сертификатом:
Admin/system@nodename# set settings certificates <certificate-name>
Доступны параметры:
Параметр
Описание
name
Название сертификата.
description
Описание сертификата.
role
Тип сертификата:
web-cert-chain
: цепочка сертификатов веб-консоли.
web-ssl
: сертификат, использующийся для создания безопасного HTTPS-подключения администратора к веб-консоли UserGate.
none
certificate-chain
Цепочка сертификатов в формате PEM.
Для удаления сертификата:
Admin/system@nodename# delete settings certificates <certificate-name>
Команды для просмотра информации об определённом сертификате или о всех сертификатах:
Admin/system@nodename# show settings certificates
Admin/system@nodename# show settings certificates <certificate-name>
v7.x
Настройка управления доступом к консоли устройства
Настройка серверов аутентификации

## Источник

https://docs.usergate.com/nastrojka-sertifikatov_1403.html
