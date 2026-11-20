---
заголовок: Настройка профилей MFA (мультифакторной аутентификации)
url: https://docs.usergate.com/nastrojka-profilej-mfa-(mul6tifaktornoj-autentifikacii)_1711.html
получено: 2026-11-20 16:26 +0700
продукт: DCFW
версия: 8.x
раздел: Настройка профилей MFA (мультифакторной аутентификации)
id_статьи: 1711
обновлено: 18 Nov, 2024
ревизия: 1
---

# Настройка профилей MFA (мультифакторной аутентификации)

Содержание:
Technology: Identification and Authentication
Данный раздел описывает настройку профилей мультифакторной аутентификации с использованием CLI. Настройка профилей MFA производится на уровне
users mfa-profiles
. Можно создать несколько типов профилей:
MFA через TOTP
: использование токена TOTP (Time-based One Time Password) в качестве второго фактора аутентификации.
MFA через email
: использование одноразового пароля, полученного по email, в качестве второго фактора аутентификации.
MFA через SMS
: использование одноразового пароля, полученного по SMS, в качестве второго фактора аутентификации.
Для содания профиля мультифакторной аутентификации используется команда:
Admin@nodename# create users mfa-profiles <parameter>
Команда для удаления профиля мультифакторной аутентификации:
Admin@nodename# delete users mfa-profiles <mfa-name>
Для отображения информации о всех профилях или об определённом профиле MFA используются следующие команды:
Admin@nodename# show users mfa-profiles
Admin@nodename# show users mfa-profiles <mfa-name>
Настройка MFA через TOTP
Команда для добавления нового профиля мультифакторной аутентификации через TOTP:
Admin@nodename# create users mfa-profiles totp <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля MFA.
description
Описание профиля MFA.
show-qr-code
QR-код на странице Captive-портала или в электронном письме для облегчения настройки устройства или ПО TOTP клиента.
notification-profile
Выбор профиля оповещения.
notification-sender
Отправитель сообщения. Указать имя (в случае использования SMPP-профиля) или email (в случае использования SMTP-профиля).
notification-subject
Тема оповещения при использовании оповещений по email.
notification-body
Тело письма. В письме можно использовать специальную переменную {2fa_auth_code}, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками ("").
Команда для редактирования параметров профиля мультифакторной аутентификации через TOTP:
Admin@nodename# set users mfa-profiles totp <mfa-totp-name> <parameter>
Параметры, доступные для редактирования, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля мультифакторной аутентификации через TOTP:
Admin@nodename# create users mfa-profiles totp name "Test TOTP MFA profile" notification-profile pass show-qr-code on
Admin@nodename# show users mfa-profiles totp "Test TOTP MFA profile"
name                    : Test TOTP MFA profile
show-qr-code            : on
notification-profile    : pass
notification-body       : Your authentication code is {2fa_auth_code}! Do not share it with anybody!
Admin@nodename# set users mfa-profiles totp "Test TOTP MFA profile" description "Test TOTP MFA profile description"
Admin@nodename# show users mfa-profiles totp "Test TOTP MFA profile"
name                    : Test TOTP MFA profile
description             : Test TOTP MFA profile description
show-qr-code            : on
notification-profile    : pass
notification-body       : Your authentication code is {2fa_auth_code}! Do not share it with anybody!
Настройка MFA через email
Команда для добавления нового профиля мультифакторной аутентификации через email:
Admin@nodename# create users mfa-profiles smtp <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля MFA.
description
Описание профиля MFA.
notification-profile
Выбор профиля оповещения.
notification-sender
Email отправителя сообщения.
notification-subject
Тема оповещения.
notification-body
Тело письма. В письме можно использовать специальную переменную {2fa_auth_code}, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками ("").
code-lifetime
Срок действия одноразового пароля; указывается в секундах.
Команда для редактирования параметров профиля мультифакторной аутентификации через email:
Admin@nodename# set users mfa-profiles smtp <mfa-email-profile> <parameter>
Параметры, доступные для обновления, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля мультифакторной аутентификации через email:
Admin@nodename# create users mfa-profiles smtp name "Test SMTP MFA profile" notification-profile "Example SMTP profile" notification-sender sender@example.org notification-subject "Test notification subj" notification-body "Test notification text"
Admin@nodename# show users mfa-profiles smtp "Test SMTP MFA profile"
name                    : Test SMTP MFA profile
notification-profile    : Example SMTP profile
notification-sender     : sender@example.org
notification-subject    : Test notification subj
notification-body       : Test notification text
code-lifetime           : 60
Admin@nodename# set users mfa-profiles smtp "Test SMTP MFA profile" code-lifetime 70
Admin@nodename# show users mfa-profiles smtp "Test SMTP MFA profile"
name                    : Test SMTP MFA profile
notification-profile    : Example SMTP profile
notification-sender     : sender@example.org
notification-subject    : Test notification subj
notification-body       : Test notification text
code-lifetime           : 70
Настройка MFA через SMS
Команда для добавления нового профиля мультифакторной аутентификации через SMS:
Admin@nodename# create users mfa-profiles smpp <parameter>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название профиля MFA.
description
Описание профиля MFA.
notification-sender
Имя отправителя сообщения.
notification-body
Тело письма. В письме можно использовать специальную переменную {2fa_auth_code}, которая будут заменена на одноразовый пароль. Текст оповещения обособляется кавычками ("").
code-lifetime
Срок действия одноразового пароля; указывается в секундах.
Команда для редактирования параметров профиля мультифакторной аутентификации через SMS:
Admin@nodename# set users mfa-profiles smpp <mfa-sms-profile> <parameter>
Параметры, доступные для обновления, совпадают с параметрами, доступными при создании профиля.
Пример создания и редактирования профиля мультифакторной аутентификации через SMS:
Admin@nodename# create users mfa-profiles smpp name "Test SMPP MFA profile" notification-profile "Example SMPP profile" notification-sender Tes_sender notification-body "Test notification text"
Admin@nodename# show users mfa-profiles smpp "Test SMPP MFA profile"
name                    : Test SMPP MFA profile
notification-profile    : Example SMPP profile
notification-sender     : Tes_sender
notification-body       : Test notification text
code-lifetime           : 60
Admin@nodename# set users mfa-profiles smpp "Test SMPP MFA profile" code-lifetime 80
Admin@nodename# show users mfa-profiles smpp "Test SMPP MFA profile"
name                    : Test SMPP MFA profile
notification-profile    : Example SMPP profile
notification-sender     : Tes_sender
notification-body       : Test notification text
code-lifetime           : 80
v8.x
Настройка терминальных серверов
Просмотр информации об авторизованных пользователях

## Источник

https://docs.usergate.com/nastrojka-profilej-mfa-(mul6tifaktornoj-autentifikacii)_1711.html
