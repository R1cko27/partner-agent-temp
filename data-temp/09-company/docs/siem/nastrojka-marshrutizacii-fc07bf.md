---
заголовок: Настройка маршрутизации
url: https://docs.usergate.com/nastrojka-marshrutizacii_2007.html
получено: 2026-11-20 16:26 +0700
продукт: SIEM
версия: 7.x
раздел: Настройка маршрутизации
id_статьи: 2007
обновлено: 04 Dec, 2024
ревизия: 1
---

# Настройка маршрутизации

Documentation:
Technology: Routing
В данном разделе описана настройка маршрутизации с использованием интерфейса командной строки. Настройка производится на уровне
network routes
Для добавления нового статического маршрута используется команда:
Admin@nodename# create network routes <parameters>
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
Admin@nodename# create network routes name test_route description "Test static route" destination-ip 192.168.200.0/2
4 gateway 192.168.100.100 interface port1 type unicast metric 1 enabled on
Admin@nodename#
Admin@nodename# show network routes test_route
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
Admin@nodename# set network routes <route-name>
Параметры, доступные для изменения, представлены в таблице выше.
Используйте следующую команду для удаления статического маршрута:
Admin@nodename# delete network routes <route-name>
Пример удаления статического маршрута:
Admin@nodename# delete network routes test_route
Для отображения статических маршрутов:
Admin@nodename# show network routes
Шлюзы
DNS-настройки

## Источник

https://docs.usergate.com/nastrojka-marshrutizacii_2007.html
