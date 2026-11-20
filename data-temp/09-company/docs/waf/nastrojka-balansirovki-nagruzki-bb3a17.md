---
заголовок: Настройка балансировки нагрузки
url: https://docs.usergate.com/nastrojka-balansirovki-nagruzki_3012.html
получено: 2026-11-20 16:26 +0700
продукт: WAF
версия: 7.6.x
раздел: Настройка балансировки нагрузки
id_статьи: 3012
обновлено: 10 Jun, 2026
ревизия: 6
---

# Настройка балансировки нагрузки

Technology: Firewall
Настройка правил балансировки нагрузки происходит на уровне
network-policy load-balancing
с использованием языка описания политик UPL. Подробнее о структуре команд — в разделе «
UserGate Policy Language
Для отображения информации о всех балансировщиках используется команда:
Admin@nodename# show network-policy load-balancing
Настройка балансировки нагрузки на серверы публикации
Настройка правил балансировки производится на уровне
network-policy load-balancing reverse-proxy
Для создания правила балансировки:
Admin@nodename# create network-policy load-balancing reverse-proxy <position> upl-rule
Параметры правил балансировки:
Параметр
Описание
PASS
Действие для создания правила балансировки с помощью UPL.
enabled
Включение/отключение правила балансировки:
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
Описание правила балансировки.
Например:
desc("Test reverse-proxy balancing rule")
profile
Указание серверов публикации, на которые будет распределяться нагрузка. Подробнее о создании и настройке серверов публикации с использованием CLI — в разделе «
Настройка серверов публикации
Например,
profile("Reverse proxy server1", "Reverse proxy server2")
Команда для редактирования параметров правила балансировки:
Admin@nodename# set network-policy load-balancing reverse-proxy <position> upl-rule
Параметры, доступные для обновления, аналогичны параметрам, доступным при создании правила балансировки.
Команды для отображения информации о всех правилах балансировки:
Admin@nodename# show network-policy load-balancing reverse-proxy
Для отображения информации об определённом правиле балансировки:
Admin@nodename# show network-policy load-balancing reverse-proxy <position>
Пример создания правила балансировки с использованием UPL:
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
Для удаления существующего правила балансировки используется следующая команда:
Admin@nodename# delete network-policy load-balancing reverse-proxy <position>
v7.x
Настройка правил публикации
Настройки библиотек

## Источник

https://docs.usergate.com/nastrojka-balansirovki-nagruzki_3012.html
