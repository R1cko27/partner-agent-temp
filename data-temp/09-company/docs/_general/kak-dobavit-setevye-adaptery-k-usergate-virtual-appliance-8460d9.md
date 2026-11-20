---
заголовок: Как добавить сетевые адаптеры к UserGate (Virtual Appliance)?
url: https://docs.usergate.com/kak-dobavit6-setevye-adaptery-k-usergate-(virtual-appliance)_691.html
получено: 2026-11-20 16:30 +0700
продукты: UserGate NGFW, UserGate MC, UserGate LogAn
версия: 5.x, 6.x
раздел: Как добавить сетевые адаптеры к UserGate (Virtual Appliance)?
id_статьи: 691
обновлено: 04 May, 2023
ревизия: 8
крошки: Главная / Часто задаваемые вопросы / Как добавить сетевые адаптеры к UserGate (Virtual Appliance)?
---

# Как добавить сетевые адаптеры к UserGate (Virtual Appliance)?

Technology: Networking
Задача
Необходимо добавить сетевые интерфейсы в виртуальную машину.
Решение
После добавления сетевых интерфейсов на виртуальной машине необходимо перезагрузиться и при загрузке в
Boot Menu
выбрать пункт
Support menu
Refresh NIC names
, подробнее об этой и других служебных утилитах читайте в cоответствующем
разделе
руководства администратора.
Внимание!
VMware присваивает MAC-адреса в определенном порядке, а в устройствах UserGate (Virtual Appliance) сортировка интерфейсов производится по возрастанию MAC-адресов. Поэтому после выполнения Refresh NIC names необходимо проверить соответствие MAC-адресов в настройках VMWare и на устройстве UserGate. В случае необходимости, измените в настройках виртуальной машины подключение сетевых адаптеров к виртуальным сетям.
Расписание типа Повторяющиеся события
Экспорт и импорт политик UserGate через CLI

## Источник

https://docs.usergate.com/kak-dobavit6-setevye-adaptery-k-usergate-(virtual-appliance)_691.html
