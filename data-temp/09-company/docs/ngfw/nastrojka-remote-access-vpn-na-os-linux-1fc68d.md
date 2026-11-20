---
заголовок: Настройка Remote Access VPN на ОС Linux
url: https://docs.usergate.com/nastrojka-remote-access-vpn-na-os-linux_38.html
получено: 2026-11-20 16:12 +0700
продукт: NGFW
версия: 6.x, 7.x
раздел: Настройка Remote Access VPN на ОС Linux
id_статьи: 38
обновлено: 26 Nov, 2024
ревизия: 17
---

# Настройка Remote Access VPN на ОС Linux

Содержание:
Technology: VPN
Для разных дистрибутивов процедура установки VPN соединения отличается.
Для Fedora/RedHat/CentOS
Для начала необходимо установить необходимые пакеты:
sudo dnf install xl2tpd
sudo dnf install NetworkManager-l2tp
sudo dnf install NetworkManager-l2tp-gnome
Так как эти дистрибутивы используют liberswan, для корректной работы его нужно заменить. Для этого выполните команды:
sudo dnf remove libreswan
sudo dnf install strongswan
sudo service NetworkManager restart
Далее необходимо вывести l2tp из черного списка. Для этого в файле
/etc/modprobe.d/l2tp_netlink-blacklist.conf
закомментируйте следующую строчку:
blacklist l2tp_netlink
Затем в  файле
/etc/modprobe.d/l2tp_ppp-blacklist.conf закомментируйте
строчки:
blacklist l2tp_ppp
Теперь можно переходить к созданию VPN подключения.
Для Debian/Ubuntu
Выполните следующие команды:
sudo add-apt-repository ppa:nm-l2tp/network-manager-l2tp
sudo apt update
sudo apt install network-manager-l2tp network-manager-l2tp-gnome
Примечание.
В версиях Ubuntu ниже 22й, возможно придется обновить xl2tp, для этого нужно выполнить следующие команды
sudo apt remove xl2tpd
sudo add-apt-repository ppa:racb/fixes
sudo apt install xl2tpd network-manager-l2tp-gnome
Настройка VPN подключения через GUI (Графический интерфейс)
После выполнения команд выше появится возможность добавления L2TP VPN-подключения. Перейдите в
Настройки ➜ Сеть
. Добавьте
Layer 2 Tunneling Protocol (L2TP)
Далее настройте параметры подключения и укажите данные для аутентификации:
Перейдите в настройки IPsec нажатием одноимённой кнопки. В настройках IPsec укажите:
Type
: Pre-shared key (PSK).
Pre-shared key
, указанный на UserGate.
Phase1 Algorithms
: aes128-sha1-modp1024!
Phase2 Algorithm
: aes128-sha1!
Сохраните настройки IPsec. Перейдите в настройки PPP. В качестве метода аутентификации укажите PAP и отключите все виды компрессии:
Сохраните изменения. На этом настройка Ubuntu для подключения Remote Access VPN закончена.
Настройка через командную строку (CLI)
Выполните следующие действия для настройки L2TP VPN с использованием командной строки.
Выполните команду
sudo nmcli connection add connection.id vpnName con-name vpnName type VPN vpn-type l2tp connection.autoconnect no ipv4.method auto vpn.data "gateway = server_address, ipsec-enabled = yes, ipsec-esp = "aes128-sha1\!", ipsec-ike = "aes128-sha1-modp1024\!", machine-auth-type = psk, mru = 1400, mtu = 1400, no-vj-comp = yes, noaccomp = yes, nobsdcomp = yes, nodeflate = yes, nopcomp = yes, password-flags = 0, refuse-chap = yes, refuse-eap = yes, refuse-mschap = yes, refuse-mschapv2 = yes, user = username, user-auth-type = password" vpn.secrets "password = pass, ipsec-psk = key"
где
server_address
- IP-адрес VPN-сервера;
username
- имя пользователя, выполняющего подключение;
pass
- пароль учётной записи пользователя;
key
- общий ключ для установления VPN-соединения.
Организуйте туннель с помощью следующей команды:
nmcli c up vpnName
v6.x
v7.x
Также опубликовано в
Документация -> Общие сведения -> Взаимодействие со сторонними решениями
Удаленный доступ
Настройка VPN

## Источник

https://docs.usergate.com/nastrojka-remote-access-vpn-na-os-linux_38.html
