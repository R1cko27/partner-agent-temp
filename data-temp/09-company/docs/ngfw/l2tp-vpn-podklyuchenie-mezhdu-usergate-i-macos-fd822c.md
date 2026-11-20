---
заголовок: L2TP VPN-подключение между UserGate и macOS
url: https://docs.usergate.com/l2tp-vpn-podklyuchenie-mezhdu-usergate-i-macos_557.html
источник: портал документации
получено: 2026-11-20 16:13 +0700
продукт: NGFW
раздел: L2TP VPN-подключение между UserGate и macOS
id_статьи: 557
обновлено: 26 Dec, 2022
ревизия: 12
---

# L2TP VPN-подключение между UserGate и macOS

KnowledgeBase:
Далее представлены настройки для организации удалённого подключения устройств, работающих на macOS, к UserGate по протоколу L2TP.
На UserGate перейдите в раздел
VPN ➜ Профили безопасности VPN
и произведите настройку профилей безопасности:
В общем случае устройства с операционной системой macOS не требуют дополнительной настройки. В случае, если не удалось установить соединение, необходимо выбрать протокол PAP для аутентификации. Для этого выполните в терминале следующие команды:
echo refuse-chap > ~/.ppprc
echo refuse-mschap >> ~/.ppprc
echo refuse-mschap-v2 >> ~/.ppprc
Результатом выполнения команд является создание файла ~/.ppprc cо следующим содержимым:
refuse-chap
refuse-mschap
refuse-mschap-v2
v5.x
v6.x
v7.x
Также опубликовано в
Документация -> Общие сведения -> Взаимодействие со сторонними решениями
Пример настройки Site-to-Site VPN с L2TP/IPSec(IKEv1)
Авторизация

## Источник

https://docs.usergate.com/l2tp-vpn-podklyuchenie-mezhdu-usergate-i-macos_557.html
