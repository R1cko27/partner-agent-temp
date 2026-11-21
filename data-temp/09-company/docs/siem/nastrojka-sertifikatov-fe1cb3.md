---
заголовок: Настройка сертификатов
url: https://docs.usergate.com/nastrojka-sertifikatov_1453.html
источник: портал документации
получено: 2026-11-20 16:26 +0700
продукт: SIEM
версия: 7.1.x
раздел: Настройка сертификатов
id_статьи: 1453
обновлено: 25 Mar, 2024
ревизия: 1
---

# Настройка сертификатов

Documentation:
Раздел
Сертификаты
находится на уровне
settings certificates
Для импорта сертификатов предназначена команда:
Admin@nodename# import settings certificates
Далее необходимо указать параметры:
Параметр
Описание
name
Название сертификата, под которым он будет отображен в списке сертификатов.
description
Описание сертификата.
certificate-data
Данные сертификата в формате PEM.
private-key
Приватный ключ сертификата в формате PEM.
passphrase
Пароль для приватного ключа, если таковой требуется.
certificate-chain
Цепочка сертификатов вышестоящих центров сертификации, которые участвовали в создании сертификата, в формате PEM.
Для экспорта доступны сертификаты, вся цепочка сертификатов:
Admin@nodename# export settings certificates <certificate-name>
Admin@nodename# export settings certificates <certificate-name> with-chain on
С использованием командной строки возможно создание сертификата и CSR:
Admin@nodename# create settings certificates type <certificate | csr>
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
Admin@nodename# set settings certificates <certificate-name>
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
Admin@nodename# delete settings certificates <certificate-name>
Команды для просмотра информации об определённом сертификате или о всех сертификатах:
Admin@nodename# show settings certificates
Admin@nodename# show settings certificates <certificate-name>
v7.x
Настройка управления доступом к консоли устройства
Настройка серверов аутентификации

## Источник

https://docs.usergate.com/nastrojka-sertifikatov_1453.html
