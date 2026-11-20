---
заголовок: Как настроить прозрачную аутентификацию Kerberos в нескольких доменах?
url: https://docs.usergate.com/kak-nastroit6-prozrachnuyu-autentifikaciyu-kerberos-v-neskol6kih-domenah_1497.html
получено: 2026-11-20 16:19 +0700
продукт: NGFW
версия: 6.x, 7.x
раздел: Как настроить прозрачную аутентификацию Kerberos в нескольких доменах?
id_статьи: 1497
обновлено: 28 May, 2024
ревизия: 3
---

# Как настроить прозрачную аутентификацию Kerberos в нескольких доменах?

Содержание:
Technology: Identification and Authentication
Задача
Как настроить прозрачную аутентификацию Kerberos в нескольких доменах?
Решение
На самом прокси-сервере никаких дополнительных настроек производить не требуется. Для корректной работы аутентификации Kerberos в нескольких доменах необходимо настроить некоторые параметры доменов. А именно, потребуется произвести следующие настройки:
Убедиться, что между всеми деревьями и лесами доменов, а также между всеми доменами в дереве установлено транзитивное двунаправленное доверие.
Во всех доменах синхронизировано время.
Хосты во всех доменах доверяют прокси-серверу.
Возьмём для примера инфраструктуру Active Directory со следующей конфигурацией:
Хосты из всех доменов пользуются прокси-сервером с FQDN auth.corp.lab, который разрешается в IP-адрес интерфейса UserGate NGFW. Keytab-файл также создан в домене corp.local и привязан к принципалу HTTP/auth.corp.local.
Хосты из леса corp.lab, по умолчанию будут доверять запросам аутентификации Kerberos от хоста auth.corp.lab, так как все они находятся в рамках единого домена. Чтобы хосты из домена contoso.local также начали предоставлять данные аутентификации хосту из другого домена, нужно добавить FQDN прокси-сервера в зону доверенных хостов. Сделать это удобно при помощи групповых политик:
User Configuration
Policies
Administrative Templates
Windows Components
Internet Explorer
Internet Control Panel
Security Page \
Site to Zone Assignment List.
В данной конфигурации прописать FQDN прокси-сервера и задать значение 2:
User Configuration
Policies
Administrative Templates
Windows Components
Internet Explorer
Internet Control Panel
Security Page
\ Trusted Sites Zone \ Logon Options. Установить в значение "Automatic logon with current username and password".
Для браузера FireFox возможно потребуется дополнительная настройка доверенных FQDN хостов для аутентификации. Подробнее читайте в статье
Авторизация с помощью Kerberos
Загрузка сертификатов на клиентское устройство с ОС Windows 11
Лицензирование

## Источник

https://docs.usergate.com/kak-nastroit6-prozrachnuyu-autentifikaciyu-kerberos-v-neskol6kih-domenah_1497.html
