# UserGate C150 — Установка ПО

Источник: [Установка ПО](https://docs.usergate.com/hardware/C150-update.pdf).
PDF: 3 страниц. Версия: не указана; дата документа: не указана.
Способ извлечения: текстовый слой, `pypdf 7.0.1` (layout).

## Страница 1

UserGate C150
Установка ПО

UserGate C150 | Установка ПО                                           www.usergate.com

## Страница 2

УСТАНОВКА ПО USERGATE

    1.   Скачать архив ngfw_ugls_full_update_7.m.n.XXXY.tar.gz из личного кабинета My.UserGate
         (https://my.usergate.com).

      Примечание
      В результате установки прошивки настройки текущей версии UserGate будут удалены, а состояние
      устройства сброшено до первоначальной инициализации.

      USB-накопитель должен быть отформатирован в формате FAT32 как диск для хранения и переноса
      данных. На USB-накопителе не должно быть посторонних файлов.

    2.   Распаковать содержимое архива на USB-накопитель. После распаковки архива в корне накопителя
         должны присутствовать 2 директории — bin и images — и скрипт full-updater.sh                    .

      Важно!
      Перед началом процедуры устройство должно быть обесточено.

    3.   Подключить USB-накопитель к ПАК UserGate C150.
    4.   Подключить консольный кабель и подать питание на устройство.
    5.   Остановить загрузку PMC: во время загрузки системы необходимо нажать Enter после второго
         вывода сообщения (PMC) Hit 'Enter' key to stop autoboot:
             (pmc) Hit 'Enter' key to stop autoboot: 3
             Press '^]' for autoboot and connect to aux
             PMC login:
    6.   Авторизоваться под пользователем с логин/паролем: admin/password:
              PMC login: admin
              Password:
              PMC>
    7.   Запустить образ sys-recovery, выполнив следующую команду:
              PMC> autoboot recovery
              Connected to CPU at speed 115200.
              Escape character is '^]'
    8.   Дождаться запуска UGOS и авторизоваться под пользователем с логин/паролем: root/root.
               UGOS login: root
               Password:
               -----------------------------------------------------------
               UGOS NGFW 7.0.0.138A
               -----------------------------------------------------------
               root@UGOS:~#

 Установка ПО UserGate                                                                                              2 / 3

 UserGate C150

## Страница 3

9.   Смонтировать USB-накопитель с помощью следующих команд (вместо /dev/sdb1 необходимо
         указать название Вашего устройства):
                  root@UGOS:~# mkdir -p /usb && mount /dev/sdb1 /usb
                  root@UGOS:~# cd /usb
     В процессе выполнения команды mkdir возможен вывод следующего сообщения:

                   [ 71.540684] FAT-fs (sdb1): Volume was not properly unmounted.                 Some data may be corrupt.
                  Please run fsck.

     В случае появления сообщения процеду              ра обновления может быть продолжена.

    10. Запустить выполнение скрипта full-updater.sh:
                    root@UGOS:/usb# ./full-updater.sh
                    Binary file /proc/device-tree/model matches
                    ===> Copy images
                    cp 'pmc-main-C-7.0.1.826R.img'
                    cp 'pmc-loader-C-7.0.1.826R.img'
                    cp 'ugos-ugls-Model-C-boot-7.0.1.826R.img'
                    cp 'ugos-ugls-Model-C-recovery-7.0.1.826R.img'
                    cp 'ngfw-ugls-7.0.1.826R.ssd.gz'
                    ...
                    ***************************************************************************
                    Update installed successfully. Please restart device by power.
                    ***************************************************************************
                    root@UGOS:/usb#
    11. Отключить питание устройства и извлечь накопитель USB.
    12. Повторно подать питание на устройство и дождаться запуска UGOS актуальной версии                              7.0.1.XXXY:

      Примечание
      При запуске устройство самостоятельно перезагрузится несколько раз, что является штатным
      поведением после выполнения полного обновления.

               UGOS NGFW 7.0.1.826R
               Web-administrator GUI: https://127.0.0.1:8001/
               UGOS login:

 Установка ПО UserGate                                                                                                  3 / 3

 UserGate C150