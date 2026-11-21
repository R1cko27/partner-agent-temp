---
заголовок: Настройка маршрутизации
url: https://docs.usergate.com/nastrojka-marshrutizacii_1408.html
источник: портал документации
получено: 2026-11-20 16:32 +0700
продукт: Management Center
версия: 7.x
раздел: Настройка сети
id_статьи: 1408
обновлено: 21 Mar, 2024
ревизия: 4
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Настройка сети / Настройка маршрутизации
---

# Настройка маршрутизации

Documentation:
Technology: Routing
В данном разделе описана настройка маршрутизации с использованием интерфейса командной строки. Настройка производится на уровне
network routes
Для добавления нового статического маршрута используется команда:
Admin/system@nodename# create network routes <parameters>
Далее указываются параметры:
Параметр
Описание
enabled
Включение/отключение использования статического маршрута:
off
name
Имя маршрута.
description
Описание маршрута.
node-name
Выбор узла кластера для настройки маршрутизации.
type
Тип маршрута:
unicast
— стандартный тип маршрута. Пересылает трафик, адресованный на адреса назначения, через заданный шлюз.
unreachable
— трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 1).
prohibit
— трафик отбрасывается. Источнику отправляется ICMP сообщение host unreachable (type 3 code 13).
blackhole
— трафик отбрасывается (теряется), не сообщая источнику о том, что данные не достигли адресата.
destination-ip
IP-адрес подсети назначения; указывается в формате <ip/mask>.
gateway
IP-адрес шлюза, через который будет доступна указанная подсеть; этот IP-адрес должен быть доступен с устройства.
interface
Интерфейс, через который будет добавлен маршрут.
metric
Метрика маршрута. Если маршрутов в данную сеть несколько: чем меньше метрика, тем более приоритетен маршрут.
Пример добавления статического маршрута:
Admin/system@nodename# create network routes name test_route description "Test static route" destination-ip 192.168.200.0/2
4 gateway 192.168.100.100 interface port1 type unicast metric 1 enabled on
Admin/system@nodename#
Admin/system@nodename# show network routes test_route
name              : test_route
description       : Test static route
enabled           : on
node-name         : testnode1
interface         : port1
type              : unicast
destination-ip    : 192.168.200.0/24
gateway           : 192.168.100.100
metric            : 1
Чтобы изменить параметры созданного ранее статического маршрута, используйте команду:
Admin/system@nodename# set network routes <route-name>
Параметры, доступные для изменения, представлены в таблице выше.
Используйте следующую команду для удаления статического маршрута:
Admin/system@nodename# delete network routes <route-name>
Пример удаления статического маршрута:
Admin/system@nodename# delete network routes test_route
Для отображения статических маршрутов:
Admin/system@nodename# show network routes
Шлюзы
DNS-настройки

## Источник

https://docs.usergate.com/nastrojka-marshrutizacii_1408.html
