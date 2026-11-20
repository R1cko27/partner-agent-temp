---
заголовок: Настройка кластеров
url: https://docs.usergate.com/nastrojka-klasterov_3004.html
получено: 2026-11-20 16:26 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка кластеров
id_статьи: 3004
обновлено: 28 Apr, 2026
ревизия: 4
---

# Настройка кластеров

Documentation:
Technology: Clustering and HA
Настройка кластера конфигурации
Данный раздел находится на уровне
settings device-mgmt configuration-cluster
Команда обновления существующего узла кластера:
Admin@nodename# set settings device-mgmt configuration-cluster <node-name>
Доступно изменение следующих параметров:
Параметр
Описание
name
Изменить имя узла кластера
description
Обновить описание узла кластера
Задать IP-адрес интерфейса, входящего в зону, выделенную для кластера
Команды для удаления и отображения настроек узла кластера:
Admin@nodename# delete settings device-mgmt configuration-cluster <node-name>
...
Admin@nodename# show settings device-mgmt configuration-cluster <node-name>
Команда для генерации секретного кода для добавления нового узла в кластер конфигурации:
Admin@nodename# execute configurate-cluster generate-secret-key
v7.x
Настройка профилей клиентских сертификатов
Настройки раздела Пользователи и устройства

## Источник

https://docs.usergate.com/nastrojka-klasterov_3004.html
