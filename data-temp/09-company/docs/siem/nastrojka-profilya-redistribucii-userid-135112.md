---
заголовок: Настройка профиля редистрибуции UserID
url: https://docs.usergate.com/nastrojka-profilya-redistribucii-userid_1465.html
источник: портал документации
получено: 2026-11-20 16:26 +0700
продукт: SIEM
версия: 7.1.x
раздел: Настройка профиля редистрибуции UserID
id_статьи: 1465
обновлено: 25 Mar, 2024
ревизия: 1
---

# Настройка профиля редистрибуции UserID

Documentation:
Профили редистрибуции UserID предназначены для определения круга устройств UserGate, на которые отправляется информация о найденных агентом UserID пользователях.
Настройка профилей редистрибуции UserID в CLI производится на уровне
users sharing-profile
Команда для настройки:
Admin@nodename# create users sharing-profile <parameters>
При настройке необходимо установить следующие параметры:
Параметр
Описание
name
Название профиля.
description
Описание профиля (опционально).
sensors
Выбор сенсоров UserGate, на которые будет отправлена информация о пользователях.
v7.x
Настройка UserID агента
Настройка сенсоров

## Источник

https://docs.usergate.com/nastrojka-profilya-redistribucii-userid_1465.html
