---
заголовок: Настройка работы AnyDesk
url: https://docs.usergate.com/nastrojka-raboty-anydesk_673.html
источник: портал документации
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 5.x, 6.x, 7.x
раздел: Настройка работы AnyDesk
id_статьи: 673
обновлено: 27 Dec, 2024
ревизия: 5
---

# Настройка работы AnyDesk

Задача
Необходимо настроить работу AnyDesk, используется инспектирование SSL.
Решение
Создайте список URL, содержащий запись (дословно, без кавычек):
"AnyNetRelay"
, и добавьте этот список в исключения инспектирования SSL.
Примечание
AnyDesk при запросе не отправляет SNI, а при TLS-соединении отправляет CN=AnyNetRelay.
v5.x
v6.x
v7.x
Ошибка: System is booting... LOM card present
Расписание типа Повторяющиеся события

## Источник

https://docs.usergate.com/nastrojka-raboty-anydesk_673.html
