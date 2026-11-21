---
заголовок: Как разрешить работу офисной SIP АТС через UserGate?
url: https://docs.usergate.com/kak-razreshit6-rabotu-ofisnoj-sip-ats-cherez-usergate_642.html
источник: портал документации
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 6.x
раздел: Как разрешить работу офисной SIP АТС через UserGate?
id_статьи: 642
обновлено: 20 Mar, 2023
ревизия: 1
---

# Как разрешить работу офисной SIP АТС через UserGate?

Задача
Необходимо разрешить работу офисной SIP АТС через VPN UserGate.
Решение
Для решения нужно разрешить загрузку модуля SIP в командной строке UserGate NGFW при помощи следующей команды:
UTM> device config -set module_sip_enabled true
Использование нескольких идентичных контроллеров домена
Ошибка: System is booting... LOM card present

## Источник

https://docs.usergate.com/kak-razreshit6-rabotu-ofisnoj-sip-ats-cherez-usergate_642.html
