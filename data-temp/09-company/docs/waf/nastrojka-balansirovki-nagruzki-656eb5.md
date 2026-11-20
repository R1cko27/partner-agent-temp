---
заголовок: Настройка балансировки нагрузки
url: https://docs.usergate.com/nastrojka-balansirovki-nagruzki_1859.html
получено: 2026-11-20 16:25 +0700
продукт: WAF
версия: 7.x
раздел: Настройка балансировки нагрузки
id_статьи: 1859
обновлено: 21 Jan, 2025
ревизия: 3
---

# Настройка балансировки нагрузки

Technology: Firewall
Настройка правил балансировки нагрузки происходит на уровне
network-policy load-balancing
с использованием языка описания политик UPL. Подробнее о структуре команд читайте в разделе
UserGate Policy Language
Для отображения информации о всех балансировщиках используется команда:
Admin@nodename# show network-policy load-balancing
Настройка балансировщика reverse-прокси
Настройка правил балансировки reverse-прокси производится на уровне
network-policy load-balancing reverse-proxy
Для создания правила балансировки reverse-прокси:
Admin@nodename# create network-policy load-balancing reverse-proxy <position> upl-rule
Параметры правил балансировки нагрузки reverse-proxy:
Параметр
Описание
PASS
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
Название правила балансировки.
Например:
name("RP balancer")
desc
Описание правила.
Например:
desc("Test reverse-proxy balancing rule")
profile
Указание профилей серверов reverse-proxy, на которые будет распределяться нагрузка. Подробнее о создании и настройке серверов  reverse-proxy с использованием CLI в разделе
Настройка серверов reverse-прокси
Например,
profile("Reverse proxy server1", "Reverse proxy server2")
Команда для редактирования параметров правила балансировки reverse-прокси:
Admin@nodename# set network-policy load-balancing reverse-proxy <position> upl-rule
Параметры, доступные для обновления, аналогичны параметрам, доступным при создании правила балансировки серверов reverse-прокси.
Команды для отображения информации о всех правилах балансировки reverse-proxy:
Admin@nodename# show network-policy load-balancing reverse-proxy
Для отображения информации об определённом правиле балансировки reverse-proxy:
Admin@nodename# show network-policy load-balancing reverse-proxy <position>
Пример создания правила балансировщика нагрузки reverse-proxy с использованием UPL:
Admin@nodename# create network-policy load-balancing reverse-proxy 1 upl-rule OK \
...profile("Reverse proxy server1", "Reverse proxy server2") \
...desc("Test reverse proxy balancing rule") \
...name(test_reversep1) \
...enabled(true)
...
Admin@nodename# show network-policy load-balancing reverse-proxy
% ----------------- 1 -----------------
OK \
profile("Reverse proxy server1", "Reverse proxy server2") \
desc("Test reverse proxy balancing rule") \
enabled(true) \
id("1ed892bb-26ee-4ab1-8a55-2f412ce8b55a") \
name(test_reversep1)
Для удаления существующего правила балансировки нагрузки reverse-proxy используется следующая команда:
Admin@nodename# delete network-policy load-balancing reverse-proxy <position>
v7.x
Настройка правил межсетевого экрана
Настройки глобального портала

## Источник

https://docs.usergate.com/nastrojka-balansirovki-nagruzki_1859.html
