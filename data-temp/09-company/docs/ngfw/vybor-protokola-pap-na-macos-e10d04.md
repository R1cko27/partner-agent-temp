---
заголовок: Выбор протокола PAP на MacOs
url: https://docs.usergate.com/vybor-protokola-pap-na-macos_559.html
получено: 2026-11-20 16:14 +0700
продукт: NGFW
раздел: Выбор протокола PAP на MacOs
id_статьи: 559
обновлено: 22 Feb, 2023
ревизия: 3
---

# Выбор протокола PAP на MacOs

KnowledgeBase:
Задача
При настройке VPN на клиентском компьютере необходимо указать протокол PAP для авторизации пользователя.
Решение
На устройствах с операционной системой MacOS запретите использование протоколов авторизации, отличных от PAP. Для этого выполните в терминале следующие команды:
echo refuse-chap > ~/.ppprc
echo refuse-mschap >> ~/.ppprc
echo refuse-mschap-v2 >> ~/.ppprce>
Результатом выполнения команд является создание файла ~/ppprc cо следующим содержимым:
refuse-chap
refuse-mschap
refuse-mschap-v2
v5.x
v6.x
v7.x
Ошибки TLS в журнале веб-доступа
Избыточные записи о срабатываниях правил контентной фильтрации в...

## Источник

https://docs.usergate.com/vybor-protokola-pap-na-macos_559.html
