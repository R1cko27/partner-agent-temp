---
заголовок: Автоматизация развертывания UserGate NGFW с помощью Cloud-init
url: https://docs.usergate.com/avtomatizaciya-razvertyvaniya-usergate-ngfw-s-pomosh6yu-cloud-init_393.html
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 7.0.1, 7.1.0
раздел: Автоматизация развертывания UserGate NGFW с помощью Cloud-init
id_статьи: 393
обновлено: 05 Mar, 2024
ревизия: 11
---

# Автоматизация развертывания UserGate NGFW с помощью Cloud-init

Documentation:
Cloud-init — индустриальный стандарт для кросс-платформенной инициализации виртуальных машин (инстансов) в облаках провайдеров. Межсетевой экран UserGate поддерживает возможность первоначальной настройки с помощью механизма Cloud-init. Настройка межсетевого экрана осуществляется с помощью двух модулей:
Настройка с помощью команд CLI (файл с заголовком #utm-config). Возможно использовать все CLI-команды для полной настройки инстанса.
Активация лицензии (файл с заголовком #utm-license).
Другие модули Cloud-init не поддерживаются.
Пример файла конфигурации с CLI командами (user-data):
#utm-config
#set password for initial Administrator (Admin). Obligatory comand.
password 123
#Set addresses and settings for network interfaces:
set network interface adapter port1 \
ip-addresses [ 172.16.6.9/24 ] \
enabled on \
zone "Trusted"
set network interface adapter port2 \
ip-addresses [ 172.16.8.9/24 ] \
enabled on \
zone "Untrusted"
set network interface adapter port3 \
ip-addresses [ 172.16.7.9/24 ] \
enabled on \
zone "DMZ"
#Create network gateway to Internet:
create network gateway \
ip 172.16.8.2 \
default on \
interface port2 \
virtual-router default \
enabled on
#Create firewall rule to allow traffic from Trusted to untrusted security zones:
create network-policy firewall \
position 1 upl-rule ALLOW \
src.zone = Trusted \
dst.zone = Untrusted \
enabled(true) \
name("Cloud-Init: Allow from Trusted to Untrusted")
В данный файл можно добавлять все доступные для администратора команды CLI. Подробно о CLI-командах смотрите в разделе
Интерфейс командной строки (CLI)
# — обозначает начало комментария, обратный слэш — переход на следующую строку.
Если необходимо активировать создаваемый инстанс, то это можно сделать через указание параметров для лицензирования в отдельном файле. Следует учитывать, что активация возможна только при наличии у инстанса доступа в сеть интернет. Пример содержимого файла для активации лицензии (vendor-data):
#utm-license
pin_code: UGN4-XXXX-YYYY-ZZZZ-AAAA
reg_name: UG-test
email:  email@company.com
user_name: Alexander
last_name: Petrov
company: UserGate
country: Russia
region: Novosibirsk
Оба файла можно объединить в один файл, используя multipart формат:
Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0
--//
Content-Type: text/utm-config; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="config.txt"
#utm-config
password 123
set network interface adapter port1 \
ip-addresses [ 172.16.6.9/24 ] \
enabled on \
zone "Trusted"
set network interface adapter port2 \
ip-addresses [ 172.16.8.9/24 ] \
enabled on \
zone "Untrusted"
set network interface adapter port3 \
ip-addresses [ 172.16.7.9/24 ] \
enabled on \
zone "DMZ"
create network gateway \
ip 172.16.8.2 \
default on \
interface port2 \
virtual-router default \
enabled on
create network-policy firewall \
position 1 upl-rule ALLOW \
src.zone = Trusted \
dst.zone = Untrusted \
enabled(true) \
name("Cloud-Init: Allow from Trusted to Untrusted")
--//
Content-Type: text/utm-license; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="license.txt"
#utm-license
pin_code: UGN4-XXXX-YYYY-ZZZZ-AAAA
reg_name: UG-test
email:  email@company.com
user_name: Alexander
last_name: Petrov
company: UserGate
country: Russia
region: Novosibirsk
--//
Настройки могут быть переданы в NGFW:
Методами, реализуемыми облачными провайдер, например, у провайдера Digital Ocean при создании виртуальной машины (droplet) настройки необходимо вставить в опциональное поле
User data
Select additional options ➜ User data
). Аналогичным образом настройки можно передать и у других поставщиков облачных услуг.
Через подключаемый iso-диск. Диск должен содержать файлы meta-data, user-data, vendor-data следующего содержимого:
meta-data:
instance-id: vm1
user-data — с CLI-командами настройки инстанса:
#utm-config
#set password for initial Administrator (Admin). Obligatory comand.
password 123
#Set addresses and settings for network interfaces:
set network interface adapter port1 \
ip-addresses [ 172.16.6.9/24 ] \
enabled on \
zone "Trusted"
...
vendor-data — с информацией о лицензировании (опционально):
#utm-license
pin_code: UGN4-XXXX-YYYY-ZZZZ-AAAA
reg_name: UG-test
email: email@company.com
...
Для создания iso-диска в Linux можно использовать следующую утилиту:
mkisofs -joliet -rock -volid "cidata" -output nocloud.iso meta-data user-data vendor-data
Полученный iso-диск необходимо подключить к виртуальной машине UserGate. После успешной первой загрузки виртуальная машина получит все настройки, указанные для нее в созданных файлах.
v7.x
Подключение к UserGate NGFW
Лицензирование

## Источник

https://docs.usergate.com/avtomatizaciya-razvertyvaniya-usergate-ngfw-s-pomosh6yu-cloud-init_393.html
