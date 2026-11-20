---
заголовок: Автоматизация развертывания UserGate SWG с помощью Cloud-init
url: https://docs.usergate.com/avtomatizaciya-razvertyvaniya-usergate-swg-s-pomosh6yu-cloud-init_2556.html
получено: 2026-11-20 16:22 +0700
продукт: SWG
версия: 7.5.x
раздел: Автоматизация развертывания UserGate SWG с помощью Cloud-init
id_статьи: 2556
обновлено: 25 Feb, 2026
ревизия: 4
---

# Автоматизация развертывания UserGate SWG с помощью Cloud-init

Cloud-init — индустриальный стандарт для кросс-платформенной инициализации виртуальных машин (инстансов) в облачных сервисах провайдеров. UserGate SWG поддерживает возможность первоначальной настройки с помощью механизма Cloud-init. Настройка межсетевого экрана осуществляется с помощью двух модулей:
С помощью команд CLI (файл с заголовком #utm-config). Возможно использовать все CLI-команды для полной настройки виртуальной машины.
Посредством активации лицензии (файл с заголовком #utm-license).
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
# — обозначает начало комментария, обратный слеш — переход на следующую строку.
В данный файл можно добавлять все доступные для администратора команды CLI. Подробнее о CLI-командах — в разделе «
Интерфейс командной строки (CLI)
Активировать создаваемую виртуальную машину можно через указание параметров для лицензирования в отдельном файле. Следует учитывать, что активация возможна только при наличии у виртуальной машины доступа в сеть интернет. Пример содержимого файла для активации лицензии (vendor-data):
#utm-license
pin_code: UGN4-XXXX-YYYY-ZZZZ-AAAA
reg_name: UG-test
email:  email@company.com
user_name: Alexander
last_name: Petrov
company: UserGate
country: Russia
region: Novosibirsk
Оба файла можно объединить в один файл, используя формат multipart:
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
Настройки могут быть переданы в SWG:
Через облачный провайдер. Например, в провайдере Digital Ocean при создании виртуальной машины (droplet) настройки необходимо вставить в опциональное поле
User data
Select additional options ➜ User data
). Аналогичным образом настройки можно передать и через другие поставщики облачных услуг.
Через подключаемый ISO-диск. На диске должны быть файлы
meta-data
user-data
vendor-data
со следующим содержимым:
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
Для создания ISO-диска на Linux можно использовать следующую утилиту:
mkisofs -joliet -rock -volid "cidata" -output nocloud.iso meta-data user-data vendor-data
Полученный ISO-диск необходимо подключить к виртуальной машине UserGate. После успешной первой загрузки виртуальная машина получит все настройки, указанные для нее в созданных файлах.
v7.x
Развертывание виртуального образа
Требования к сетевому окружению

## Источник

https://docs.usergate.com/avtomatizaciya-razvertyvaniya-usergate-swg-s-pomosh6yu-cloud-init_2556.html
