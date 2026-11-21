---
заголовок: Настройка VPN туннеля между UserGate NGFW и Cisco ASR1002-X
url: https://docs.usergate.com/nastrojka-vpn-tunnelya-mezhdu-usergate-ngfw-i-cisco-asr1002-x_729.html
источник: портал документации
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 6.x, 7.x
раздел: Настройка VPN туннеля между UserGate NGFW и Cisco ASR1002-X
id_статьи: 729
обновлено: 14 Jun, 2023
ревизия: 7
---

# Настройка VPN туннеля между UserGate NGFW и Cisco ASR1002-X

Содержание:
KnowledgeBase:
Technology: VPN
Описание
Рассмотрим ситуацию, при которой необходимо объединить две сети, одна из которых защищена с помощью UserGate NGFW, а другая – с помощью Cisco ASR1002-X.
В данном примере предполагается использование следующих адресов:
Адрес сети, защищенной UserGate NGFW: 172.21.10.0/24.
IP-адрес внешнего интерфейса UserGate NGFW: 91.107.67.230.
IP-адрес туннельного интерфейса tunnel4: 172.21.10.254/24.
Адрес сети, защищенной Cisco ASR1002-X: 172.22.10.0/24.
IP-адрес внешнего интерфейса Cisco ASR1002-X: 91.107.67.229.
Схема сети
Настройка на стороне Cisco ASR1002-X
Задать параметры 1-й фазы соласования туннеля:
crypto isakmp policy 235
encr aes
authentication pre-share
group 14
Задать pre-shared key:
crypto isakmp key <PSK ключ> address 91.107.67.230
Задать параметры 2-й фазы соласования туннеля:
crypto ipsec transform-set UserGate_TEST esp-aes 256 esp-sha256-hmac
mode tunnel
Создать фильтр для сетей, между которыми будет шифроваться трафик (src/dst):
ip access-list extended UserGate_TEST
permit ip 172.22.10.0 0.0.0.255 172.21.10.0 0.0.0.255
Создать криптокарту, которая будет назначена на исходящий интерфейс:
crypto map IPSEC 100 ipsec-isakmp
description UserGate_TEST
set peer 91.107.67.230
set transform-set UserGate_TEST
match address UserGate_TEST
Эмуляция внутренней сети:
interface Port-channel1.3970
description UserGate_TEST
encapsulation dot1Q 3970
ip address 172.22.10.1 255.255.255.0
Создать маршрут до локальной сети за туннелем UserGate:
ip route 172.21.10.0 255.255.255.0 91.107.67.225
Назначить созданную криптокарту на исходящий интерфейс:
interface Port-channel1.100
crypto map IPSEC
Настройка на стороне Cisco завершена.
Настройка на стороне UserGate NGFW
В разделе
Сеть
Зоны
разрешить доступ по VPN для зоны Untrusted:
В разделе
Сеть
Интерфейсы
создать интерфейс tunnel4 и назначить адрес из пула локальной сети 172.21.10.254:
В разделе
VPN
Профили безопасности VPN
создать новый профиль безопасности VPN со следующими параметрами:
В разделе
VPN
Клиентские правила
создать правило CISCO IPsec, выбрав созданный ранее профиль безопасности VPN. В поле адреса сервера указать IP-адрес внешнего интерфейса Cisco ASR1002-X. В поле протокола VPN выбрать IPsec-туннель. Далее указать разрешенные подсети со стороны UserGate и Cisco:
В разделе
Сеть
Виртуальные маршрутизаторы
Виртуальный маршрутизатор по умолчанию
прописать статический маршрут к удаленной локальной сети Cisco через tunnel4:
В разделе
Политики сети
Межсетевой экран
создать двустороннее правило доступа с указанием Trusted и VPN Site-to-Site зон. Разрешить трафик между Trusted и S2S:
Проверить доступность удаленной сети. Для этого отправить icmp запрос с Trusted-интерфейса в сторону интерфейса локальной сети Cisco:
Настройка на стороне UserGate завершена.
v6.x
v7.x
Также опубликовано в
Документация -> Общие сведения -> Взаимодействие со сторонними решениями
Настройка VPN-соединения между UserGate и FortiGate
Настройка VPN с передачей маршрутов по OSPF для своевременного...

## Источник

https://docs.usergate.com/nastrojka-vpn-tunnelya-mezhdu-usergate-ngfw-i-cisco-asr1002-x_729.html
