---
заголовок: Настройка правил инспектирования туннелей
url: https://docs.usergate.com/nastrojka-pravil-inspektirovaniya-tunnelej_824.html
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка правил инспектирования туннелей
id_статьи: 824
обновлено: 14 May, 2025
ревизия: 8
---

# Настройка правил инспектирования туннелей

Documentation:
Настройка правил инспектирования туннелей производится на уровне
security-policy tunnel-inspection
. Подробнее о структуре команд читайте в разделе
UserGate Policy Language
Для создания правила инспектирования туннелей используется команда:
Admin@nodename# create security-policy tunnel-inspection <position> upl-rule
Параметры правил инспектирования туннелей:
Параметр
Описание
PASS
Действие правила инспектирования туннелей:
— Инспектировать.
PASS
— Не расшифровывать
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила инспектирования туннелей.
Например:
name("Tunnel inspection rule example")
desc
Описание правила.
Например:
desc("Tunnel inspection rule example configured via CLI")
service
Тип туннеля:
service = gre
: инспектирование туннелей GRE.
service = gtpu
: инспектирование туннелей GTP-U.
service = ipsec_null
: инспектирование нешифрованных IPsec-туннелей
src.zone
Зона источника трафика.
Для указания зоны источника, например, Trusted:
src.zone = Trusted
Подробнее о настройке зон с использованием интерфейса командной строки читайте в разделе
Зоны
src.ip
Добавление списков IP-адресов или доменов источника.
Для указания списка IP-адресов:
src.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI читайте в разделе
Настройка IP-адресов
Для указания списка доменов источника:
src.ip = lib.url()
; в скобках необходимо указать название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки читайте в разделе
Настройка списков URL
src.geoip
Указание GeoIP источника; необходимо указать код страны (например,
src.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15.
dst.zone
Зона назначения трафика, например,
dst.zone = "Tunnel inspection zone"
Подробнее о настройке зон с использованием интерфейса командной строки читайте в разделе
Зоны
dst.ip
Добавление списков IP-адресов или доменов назначения.
Для указания списка IP-адресов:
dst.ip =
lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI читайте в разделе
Настройка IP-адресов
Для указания списка доменов назначения:
dst.ip =
lib.url()
; в скобках необходимо указать название URL-списка, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки читайте в разделе
Настройка списков URL
dst.geoip
Указание GeoIP назначения; необходимо указать код страны (например,
dst.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15.
Для редактирования правил инспектирования туннелей используется команда:
Admin@nodename# set security-policy tunnel-inspection <position> upl-rule
Для просмотра всех созданных правил инспектирования туннелей используется команда:
Admin@nodename# show security-policy tunnel-inspection
Для просмотра определенного правила инспектирования туннелей используется команда:
Admin@nodename# show security-policy tunnel-inspection <position>
Пример создания правила инспектирования туннелей:
Admin@nodename# create security-policy tunnel-inspection 1 upl-rule PASS \
...src.zone = Untrusted \
...dst.zone = Trusted \
...service = ipsec_null \
...name("Test tunnel-inspection rule") \
...desc("Test nunnel-inspection rule description") \
...enabled(true)
...
Admin@nodename# show security-policy tunnel-inspection 1
% ----------------- 1 -----------------
PASS \
src.zone = Untrusted \
dst.zone = Trusted \
service = ipsec_null \
desc("Test nunnel-inspection rule description") \
enabled(true) \
id("051cf677-3d36-4d5c-968f-73c3421c2b28") \
name("Test tunnel-inspection rule")
Для удаления правила инспектирования туннелей используется команда:
Admin@nodename# delete security-policy tunnel-inspection <position>
v7.x
Настройка веб-безопасности
Настройка инспектирования SSL

## Источник

https://docs.usergate.com/nastrojka-pravil-inspektirovaniya-tunnelej_824.html
