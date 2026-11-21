---
заголовок: Загрузка сертификатов на клиентское устройство с ОС Windows 11
url: https://docs.usergate.com/zagruzka-sertifikatov-na-klientskoe-ustrojstvo-s-os-windows-11_1053.html
источник: портал документации
получено: 2026-11-20 16:31 +0700
раздел: Авторизация и аутентификация
id_статьи: 1053
обновлено: 09 Jan, 2024
ревизия: 4
крошки: Главная / Часто задаваемые вопросы / Авторизация и аутентификация / Загрузка сертификатов на клиентское устройство с ОС Windows 11
---

# Загрузка сертификатов на клиентское устройство с ОС Windows 11

Содержание:
Technology: Identification and Authentication
Задача
Как автоматизировать загрузку сертификатов на клиентское устройство с ОС Windows 11.
Решение
При тестировании технических решений бывает необходимо автоматизировать процесс загрузки пользовательских сертификатов на клиентское устройство с ОС Windows. Часто для этих целей в скриптах используется системная утилита certutil. Однако в Windows 11 утилита certutil загружает пользовательский сертификат некорректно. В качестве альтернативного метода загрузки сертификата на клиентском устройстве с ОС Windows 11 можно использовать следующую последовательность команд в PowerShell:
$pfx = new-object System.Security.Cryptography.X509Certificates.X509Certificate2
$pfx.import("C:\cert.pfx","1234","MachineKeySet, PersistKeySet")
$store = new-object System.Security.Cryptography.X509Certificates.X509Store("My","LocalMachine")
$store.open("MaxAllowed")
$store.add($pfx)
$store.close()
Подробнее об использованных атрибутах смотрите в статье:
https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.x509certificates.x509keystorageflags?view=net-8.0
Проблемы с авторизацией при использовании нескольких методов...
Как настроить прозрачную аутентификацию Kerberos в нескольких...

## Источник

https://docs.usergate.com/zagruzka-sertifikatov-na-klientskoe-ustrojstvo-s-os-windows-11_1053.html
