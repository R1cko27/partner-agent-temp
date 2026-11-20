---
заголовок: Фильтрация по портам
url: https://docs.usergate.com/fil6traciya-po-portam_1729.html
получено: 2026-11-20 16:25 +0700
продукт: DCFW
версия: 8.x
раздел: Фильтрация по портам
id_статьи: 1729
обновлено: 18 Nov, 2024
ревизия: 1
---

# Фильтрация по портам

Для задания проверки TCP/UDP-портов используйте параметры:
.src_port
— для проверки портов источника:
.dst_port
— для проверки портов назначения:
Доступно использование следующих выражений:
Наименование
Описание
.src_port=<port_number>;
.dst_port=<port_number>;
Указание конкретного порта источника и/или назначения.
.src_port!=<port_number>;
.dst_port!=<port_number>;
Проверка всех портов кроме указанного.
.src_port=:<port_number>;
.dst_port=:<port_number>;
Проверка всех портов, номер которых меньше или равен номеру указанного порта.
.src_port!=:<port_number>;
.dst_port!=:<port_number>;
Проверка всех портов, номер которых больше указанного.
.src_port=<port_number>:;
.dst_port=<port_number>:;
Проверка всех портов, номер которых больше или равен номеру указанного порта.
.src_port!=<port_number>:;
.dst_port!=<port_number>:;
Проверка всех портов, номер которых меньше указанного.
.src_port=<port_number1>:<port_number2>;
.dst_port=<port_number1>:<port_number2>;
Проверка портов, находящихся в указанном диапазоне (port_number1 и port_number2 включительно).
.src_port!=<port_number1>:<port_number2>;
.dst_port!=<port_number1>:<port_number2>;
Проверка всех портов, не входящих в указанный диапазон (т.е. проверяются порты с номерами менее port_number1 и более port_number2).
v8.x
Фильтрация по IP-адресам
Сканирование пакетов без полезной нагрузки

## Источник

https://docs.usergate.com/fil6traciya-po-portam_1729.html
