---
заголовок: UserGate B50 — Обновление компонентов ПО через PMC
url: https://docs.usergate.com/hardware/sw-update-over-pmc.pdf
источник: docs.usergate.com / static.usergate.com (PDF)
продукт: Платформа B50
версия: 7.x
раздел: Аппаратные платформы
обновлено: 2026/07/08
страниц: 15
получено: 2026-11-21
---

# UserGate B50 — Обновление компонентов ПО через PMC

Источник: [Обновление компонентов ПО через PMC](https://docs.usergate.com/hardware/sw-update-over-pmc.pdf).
PDF: 15 страниц. Версия: 7.x; дата документа: 2026/07/08.
Способ извлечения: текстовый слой, `pypdf 7.0.1` (layout).

## Страница 1

Обновление компонентов ПО для
аппаратных платформ

## Страница 2

Оглавление

- Процедура обновления
  - Ручное обновление компонентов ПО с использованием PMC

## Страница 3

ПРОЦЕДУРА ОБНОВЛЕНИЯ

Ручное обновление компонентов ПО с
использованием PMC

Некоторые модели аппаратных платформ UserGate оснащены модулем PMC
(Platform Management Controller), предназначенным для мониторинга состояния
платформы и управления ее аппаратными компонентами.

Если устройство становится недоступным по основному интерфейсу
управления, доступ к модулю PMC можно получить одним из следующих
способов:

- через выделенный сетевой интерфейс MGMT в режиме PMC CLI;

- через консольный порт USB Type-C.

С помощью PMC можно обновить все программные компоненты программно-
аппаратного комплекса (ПАК), за исключением основного образа продукта
(UGOS).

Программные компоненты устройства:

- pmc — основная прошивка модуля PMC. Используется для мониторинга
     состояния платформы и управления ее аппаратными компонентами.

- pmc-backup — резервная прошивка PMC. Может быть загружена из
     режима загрузчика с помощью команды autoboot backup. Для
     обновления используется тот же образ прошивки, что и для компонента
     pmc.

- boot — загрузчик (bootloader) хост-процессора платформы. Выполняет
     начальную инициализацию оборудования и запуск операционной системы.

- sys-recovery — минимальный образ UGOS, предназначенный для
     первоначальной установки основного образа системы, а также для
     аварийного восстановления работоспособности устройства.

- ncpmc — прошивка контроллера PMC, установленного на сетевой плате.
     Присутствует только на платформе UserGate FG. Во время обновления

## Страница 4

этого компонента временно отключаются все вторичные источники
      питания платформы.

 Для подключения к PMC с помощью SSH через интерфейс MGMT потребуется
 эмулятор терминала (например, minicom или Putty). При первичной
 инициализации используйте IP-адрес по умолчанию: 192.168.1.2.

 Подробнее о PMC CLI — в разделе       Интерфейс командной строки PMC         .

 Обновление программных компонентов устройств через PMC можно выполнить
 одним из двух способов:

- с помощью утилиты TFTP     ;

- с помощью утилиты SCP     .

 Обновление основного образа продукта можно выполнить с
 помощью процедуры sys-recovery        или штатными средствами продукта в
 разделе обновления ПО в веб-интерфейсе.

 Обновление программных компонентов через PMC
 с использованием утилиты TFTP

 Для обновления программных компонентов с помощью утилиты TFTP:

      1. Настройте TFTP-сервер в сети, доступной через интерфейс MGMT.

      2. Скачайте в личном кабинете архив («Файл для чистой установки
      UserGate на ПАК типа С150 и FG, версия 7.x.x.xxxxxxx») и извлеките из папки
      images файлы прошивок:

- pmc-main-<model>-7.x.x.xxx.img;

- ugos-ugls-Model-C-recovery-7.x.x.xxx.img;

- ugos-ugls-Model-C-boot-7.x.x.xxx.img.

             Примечание
         Версии прошивок ugos-ugls-Model-C-recovery и ugos-ugls-Model-C-
         boot и версия операционной системы UGOS должны совпадать.

      3. Загрузите прошивки на TFTP-сервер.

## Страница 5

4. Подключитесь к PMC CLI через консоль (CON) или по SSH через
    интерфейс MGMT. Войдите в интерфейс CLI с помощью созданного ранее
    логина и пароля (по умолчанию — admin/password; начиная с версии ПО
    7.5.0 — Admin/usergate).

           Примечание
       Если при подключении по SSH через интерфейс MGMT появится ошибка,
       необходимо загрузить сертификат. Подробнее о процедуре — в разделе
       Загрузка сертификата.

    5. Войдите в режим конфигурирования устройства. Этот пункт следует
    выполнять только для версий ПО старше 7.1.0:

PMC> configure
PMC#

    6. Остановите процессор:

PMC# set platform soc stop
SoC stoped

    7. При необходимости настройте сеть на MGMT-интерфейсе:

PMC# set network ip 192.168.1.2/24
Set ip address complete
PMC# set network gateway 192.168.1.1
Set gateway complete
PMC#

    8. Проверьте установленную версию образа контроллера и сравните с
    последней доступной версией:

PMC> version
PMC(Main) Firmware 7.0.1 build 20R (2023-03-22 — 10:18:23)

## Страница 6

9. Если версия прошивки не соответствует последней доступной, ее
       необходимо обновить. Укажите в команде настроенный ранее TFTP-
       сервер и файл для обновления:

  PMC# update firmware pmc tftp 192.168.1.1 pmc-main-
  <model>-7.x.x.xxx.img
  TFTP from server 192.168.1.1; our IP address is 192.168.1.2
  Filename 'pmc-main-<model>-7.x.x.xxx.img'.
  Update at QSPI offset: 0x07080000.
  Updating...

  Bytes transferred = 319280 (0x4DF30) in 3 seconds (103 KiB/s)
  TFTP update OK
  PMC#

       10. Перезапустите устройство:

  PMC# reset
  Device will be reset. Continue? (y/n): y

  PMC(Loader) Firmware 7.0.1 build 20R (2023-03-22 — 10:18:23)

       11. Войдите в PMC CLI. Логин/пароль по умолчанию — admin/password
       (начиная с версии ПО 7.5.0 — Admin/usergate):

  PMC login: Admin
  Password:
  PMC>

       12. Войдите в режим конфигурирования устройства:

  PMC> configure
  PMC#

       13. Остановите процессор:

## Страница 7

PMC# set platform soc stop

     14. Обновите образ загрузчика UGOS до последней доступной версии:

 PMC# update firmware boot tftp 192.168.1.7 ugos-ugls-Model-C-
 boot-7.x.x.xxx.img
 TFTP from server 192.168.1.7; our IP address is 192.168.1.2
 Filename ugos-ugls-Model-C-boot-7.x.x.xxx.img.
 Update at QSPI offset: 0x00000000.
 Updating...

 Bytes transferred = 5312345 (0x510F59) in 33 seconds (157 KiB/s)
 TFTP update OK

     15. Обновите образ sys-recovery до последней доступной версии:

 PMC# update firmware sys-recovery tftp 192.168.1.7 ugos-ugls-Model-C-
 recovery-7.x.x.xxx.img
 TFTP from server 192.168.1.7; our IP address is 192.168.1.2
 Filename 'ugos-ugls-Model-C-recovery--7.x.x.xxx.img'.
 Update at QSPI offset: 0x01000000.
 Updating...

 Bytes transferred = 52895516 (0x3271F1C) in 262 seconds (197 KiB/s)
 TFTP update OK

 PMC> reset

Обновление программных компонентов через
PMC с использованием утилиты SCP

Для обновления программных компонентов с помощью утилиты SCP:

     1. Скачайте в личном кабинете архив («Файл для чистой установки UserGate
     на ПАК типа С150 и FG, версия 7.x.x.xxxxxxx») и извлеките из папки images
     файлы прошивок:

- pmc-main-<model>-7.x.x.xxx.img,

## Страница 8

- ugos-ugls-Model-C-recovery-7.x.x.xxx.img,

- ugos-ugls-Model-C-boot-7.x.x.xxx.img.

             Примечание
          Версии прошивок ugos-ugls-Model-C-recovery и ugos-ugls-Model-C-
          boot и версия операционной системы UGOS должны совпадать.

       2. Включите устройство и дождитесь его полной загрузки, или остановите
       запуск на этапе запуска PMC. В процессе запуска устройства функция
       обновления ПО недоступна.

  (pmc) Hit 'Enter' key to stop autoboot:  2

  Press '^]' for autoboot and connect to aux
  PMC login:

       3. Подключитесь к PMC CLI через консоль (CON) или по SSH через
       интерфейс MGMT. Войдите в интерфейс CLI с использованием созданного
       ранее пользователя и пароля (по умолчанию — admin/password; начиная с
       версии ПО 7.5.0 — Admin/usergate):

  PMC login: Admin
  Password:
  PMC>

             Примечание
          Если при подключении по SSH через интерфейс MGMT появится ошибка,
          необходимо загрузить сертификат. Подробнее о процедуре — в разделе
          Загрузка сертификата.

       4. Войдите в режим конфигурирования устройства:

  PMC> configure
  PMC#

## Страница 9

5. Настройте сетевые параметры в PMC, указав адрес и шлюз по
    умолчанию вручную, или включив DHCP:

PMC# set network dhcp on
DHCP client start complete
PMC#

    6. Если используется DHCP, убедитесь, что параметры сети были получены:

PMC# show network status
------------------------------------
Network status:
IP address type: dhcp
IP address: 192.168.1.2
Gateway address: 192.168.1.1
Netmask: 255.255.255.0
------------------------------------
PMC#

    7. Проверьте версию образа контроллера и сравните с последней
    доступной версией:

PMC> version
PMC(Main) Firmware 7.x.x build YYY

    8. Если версия не совпадает, требуется обновить прошивку контроллера
    до последней доступной версии. Укажите в команде настроенный ранее на
    устройстве IP-адрес:

scp pmc-main-<model>-7.x.x.xxx.img Admin@192.168.1.2:/firmware/pmc
Admin@192.168.1.2's password:
pmc-main-<model>-7.x.x.xxx.img
100% 6144KB 249.3KB/s   00:24

    9. Перезапустите устройство:

## Страница 10

PMC# reset
  Device will be reset. Continue? (y/n): y

  PMC(Loader) Firmware 7.0.1 build 20R (2023-03-22 — 10:18:23)

       10. Войдите в PMC CLI (по умолчанию — admin/password; начиная с версии
       ПО 7.5.0 — Admin/usergate):

  PMC login: Admin
  Password:
  PMC>

       11. Войдите в режим конфигурирования устройства:

  PMC> configure
  PMC#

       12. Остановите процессор:

  PMC# set platform soc stop

       13. Обновите образ загрузчика UGOS до последней доступной версии:

  scp ugos-ugls-Model-C-boot-7.x.x.xxx.img Admin@192.168.1.2:/firmware/
  boot
  Admin@192.168.1.2's password:
  ugos-ugls-Model-C-boot-7.x.x.xxx.img
  100% 6144KB 249.3KB/s   00:24

       14. Обновите образ sys-recovery до последней доступной версии:

  scp ugos-ugls-Model-C-recovery-7.x.x.xxx.img Admin@192.168.1.2:/
  firmware/sys-recovery
  Admin@192.168.1.2's password:

## Страница 11

ugos-ugls-Model-C-recovery-7.x.x.xxx.img
 100% 6144KB 249.3KB/s   00:24

     15. Подключитесь к устройству и перезапустите его:

 PMC# reset
 Device will be reset. Continue? (y/n): y

 PMC(Loader) Firmware 7.0.1 build 20R (2023-03-22 — 10:18:23)

Обновление UGOS через sys-recovery (с
использованием внешнего TFTP/FTP/HTTP/SSH-
сервера)

Эта инструкция подходит для случаев:

- когда необходимо в первый раз установить UGOS на устройство;

- необходимо полностью перезаписать образ UGOS.

Обязательные условия для обновления:

- к устройству имеется доступ по сети Ethernet;

- на устройстве установлен образ sys-recovery.

Порядок обновления:

     1. Скачайте в личном кабинете архив прошивки (file for clean installing) в
     виде файла:

- ngfw_ugls_full_update_7.x.x.xxxxxxR.tar.gz — для моделей
           C150, C151, X10, D250, FG;

- ngfw_ugrc_full_update_7.x.x.xxxxxxR.tar.gz — для модели
           В50.

     2. Распакуйте полученный архив.

     3. В распакованном архиве перейдите в папку images.

## Страница 12

4. В папке images найдите файл образа UGOS в виде:

- ngfw-ugls-7.x.x.xxx-public.ssd.gz — для моделей C150, C151,
             X10, D250, FG;

- ngfw-ugrc-7.x.x.xxx-public.ssd.gz  — для модели В50.

       5. Загрузите образ UGOS на TFTP-сервер.

       6. Подключитесь к PMC через консольный интерфейс (USB Type-C) или по
       SSH через интерфейс MGMT.

              Примечание
          Если при подключении по SSH через интерфейс MGMT появится ошибка,
          необходимо загрузить сертификат. Подробнее о процедуре — в разделе
          Загрузка сертификата.

       7. Войдите в интерфейс CLI с использованием созданного ранее
       пользователя и пароля (по умолчанию — admin/password; начиная с
       версии ПО 7.5.0 — Admin/usergate):

  PMC login: Admin
  Password:
  PMC>

       8. Войдите в режим конфигурирования устройства:

  PMC> configure
  PMC#

       9. Остановите работу CPU и запустить образ       sys-recovery:

  PMC# set platform soc stop
  SoC stoped
  PMC# autoboot recovery
  Connected to CPU at speed 115200.
  ...
  UGOS login:

## Страница 13

10. Для входа используйте логин/пароль — root/root:

UGOS login: root
Password: root

    11. Подключите устройство к локальной сети через интерфейс port0 и
    настройте IP-адрес на интерфейсе (DHCP или статический):

root@UGOS:~# dhclient port0
root@UGOS:~# ip ro
default via 192.168.75.1 dev port0
192.168.75.0/24 dev port0 proto kernel scope link src 192.168.75.217
root@UGOS:~#

    12. Загрузите обновление с настроенного ранее TFTP-сервера:

root@UGOS:~# curl tftp://192.168.1.2/ugos/ngfw-ugls-7.x.x.xxx-
public.ssd.gz -o /ugos.ssd.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time
Current
                                 Dload  Upload   Total   Spent    Left
Speed
100  766M  100  766M    0     0  2322k      0  0:05:37  0:05:37
--:--:-- 2329k
100  766M  100  766M    0     0  2322k      0  0:05:37  0:05:37
--:--:-- 2322k
root@UGOS:~#

    13. Запишите образ на SSD-накопитель с помощью одной из следующих
    команд:

- для моделей C150, C151, X10, B50:

curl file:///ugos.ssd.gz | gzip -d | dd of=/dev/sda

- для моделей D250, FG:

## Страница 14

curl file:///ugos.ssd.gz | gzip -d | dd of=/dev/nvme0n1

       Пример выполнения команды на модели FG:

  root@UGOS:~# curl file:///ugos.ssd.gz | gzip -d | dd of=/dev/nvme0n1
    % Total    % Received % Xferd  Average Speed   Time    Time     Time
  Current
                                   Dload  Upload   Total   Spent    Left
  Speed
  100  766M  100  766M    0     0  2015k      0  0:06:29  0:06:29
  --:--:--  507k
  100  766M  100  766M    0     0  2015k      0  0:06:29  0:06:29
  --:--:-- 2015k
  41943040+0 records in
  41943040+0 records out
  21474836480 bytes (20 G) copied, 395.429293 s, 52 M/s
  root@UGOS:~#

       14. Выйдите обратно в PMC CLI с помощью нажатия комбинации
       клавиш Ctrl + ]:

  root@UGOS:~# ^]
  Disconnected from CPU

  PMC#

       15. Остановите работу CPU и запустите основной образ UGOS:

  PMC# set platform soc stop
  SoC stoped
  PMC# autoboot
  ...
  UGOS login:

## Страница 15

Загрузка сертификата

Если при подключении по SSH через интерфейс MGMT появится ошибка,
необходимо загрузить сертификат. Загрузка сертификата осуществляется
только при подключении через COM-порт.

     1. Сгенерируйте сертификат для SSH:

 openssl ecparam -genkey -name prime256v1 -noout -outform DER -out
 privatekey.der

     2. Загрузите сертификат на TFTP-сервер.

     3. Подключитесь к устройству через COM-порт. Перейдите в режим PMC
     CLI. Во время загрузки устройства при появлении строки:                  «(pmc) Hit
     'Enter'  key to stop autoboot:» нажмите Enter.

     4. Обновите сертификат на устройстве c помощью TFTP-сервера. По
     окончании обновления перезагрузите устройство:

 PMC> update key ssh tftp 192.168.1.7 privatekey.der
 TFTP from server 192.168.1.7; our IP address is 192.168.1.2
 Filename 'privatekey.der'.
 Update at QSPI offset: 0x07100000.
 Updating...
 Bytes transferred = 121 (0x79) in 9 ms (13 KiB/s)
 TFTP update OK

 PMC> reset
 Device will be reset. Continue? (y/n): y

     5. После перезагрузки подключитесь через интерфейс MGMT по SSH.

 PMC login: Admin
 Password:
 PMC>
