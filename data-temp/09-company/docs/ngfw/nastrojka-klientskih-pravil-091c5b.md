---
заголовок: Настройка клиентских правил
url: https://docs.usergate.com/nastrojka-klientskih-pravil_786.html
источник: портал документации
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка клиентских правил
id_статьи: 786
обновлено: 14 May, 2025
ревизия: 12
---

# Настройка клиентских правил

Documentation:
Technology: VPN
Клиентские правила настраиваются на уровне
vpn client-rules
. Подробнее о структурах команд настройки клиентских правил читайте в разделе
UserGate Policy Language
Команда для создания клиентского правила VPN:
Admin@nodename# create vpn client-rules <position> upl-rule <parameters>
При настройке правил необходимо указать:
Параметр
Описание
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
Название клиентского правила VPN.
Например,
name("VPN client rule example")
desc
Описание клиентского правила VPN.
Указывается, как
desc("VPN client rule example set in CLI")
profile
Профиль безопасности VPN, определяющий общий ключ шифрования (pre-shared key) и алгоритмы для шифрования и аутентификации. Например,
profile("Client VPN profile")
Подробнее о добавлении и настройке профилей безопасности читайте в разделе
Настройка профилей безопасности VPN
interface
VPN-интерфейс, который будет использоваться для подключения клиентов VPN. Чтобы указать интерфейс, например, tunnel1:
interface(tunnel3)
О добавлении и настройке интерфейсов VPN читайте в разделе
Настройка VPN-адаптера
server_address
IP-адрес VPN-сервера, куда подключается данный VPN-клиент. Как правило, это IP-адрес интерфейса в зоне Untrusted на NGFW, выполняющего роль VPN-сервера.
Задаётся в формате:
server_address("1.2.3.4")
При отображении правил, помимо заданных условий и свойств, будут показаны последняя ошибка VPN и статус подключения.
Пример создания клиентского правила VPN:
Admin@nodename# create vpn client-rules 2 upl-rule OK\
...name("Test VPN client rule") \
...desc("Test VPN client rule description") \
...profile("Client VPN profile") \
...interface(tunnel3) \
...server_address("10.10.0.1") \
...enabled(true) \
Для редактирования клиентского правила VPN:
Admin@nodename# set vpn client-rules <position> upl-rule <parameters>
Для удаления клиентского правила VPN:
Admin@nodename# delete vpn client-rules <position>
Для просмотра параметров созданных клиентских правил VPN:
Admin@nodename# show vpn client-rules <position>
v7.x
Настройка серверных правил
Настройка сетей VPN

## Источник

https://docs.usergate.com/nastrojka-klientskih-pravil_786.html
