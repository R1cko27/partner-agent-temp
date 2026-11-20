---
заголовок: Некорректная работа правил UserGate NGFW при работе с доменными пользователями
url: https://docs.usergate.com/nekorrektnaya-rabota-pravil-usergate-ngfw-pri-rabote-s-domennymi-pol6zovatelyami_675.html
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 5.x, 6.x, 7.x
раздел: Некорректная работа правил UserGate NGFW при работе с доменными пользователями
id_статьи: 675
обновлено: 04 Apr, 2023
ревизия: 7
---

# Некорректная работа правил UserGate NGFW при работе с доменными пользователями

Technology: Identification and Authentication
Задача
При изменении членства пользователя в доменных группах, UserGate NGFW не учитывает эти изменения.
Решение
Для того, чтобы UserGate NGFW обновил информацию о членстве в группах для пользователя, нужно:
В CLI выполнить команду:
cache ldap-clear
Произвести переподключение пользователя на клиентской станции (Вход-Выход).
Произвести процедуру выхода пользователю на UserGate NGFW.
После этого работа с обновленным пользователем нормализуется.
v5.x
v6.x
v7.x
Настройка браузера Chrome на Linux для авторизации...
Периодические разрывы связи при работе с потоковыми сервисами

## Источник

https://docs.usergate.com/nekorrektnaya-rabota-pravil-usergate-ngfw-pri-rabote-s-domennymi-pol6zovatelyami_675.html
