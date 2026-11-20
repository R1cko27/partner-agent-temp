---
заголовок: Настройка инспектирования SSH
url: https://docs.usergate.com/nastrojka-inspektirovaniya-ssh_826.html
источник: портал документации
получено: 2026-11-20 16:17 +0700
продукт: NGFW
версия: 7.x
раздел: Настройка инспектирования SSH
id_статьи: 826
обновлено: 02 Oct, 2024
ревизия: 10
---

# Настройка инспектирования SSH

Documentation:
Настройка правил SSH-инспектирования производится на уровне
security-policy ssh-inspection
. О структуре команд читайте подробнее в разделе
UserGate Policy Language
Для создания правила инспектирования SSH используется команда:
Admin@nodename# create security-policy ssh-inspection <position> upl-rule
Параметры правил инспектирования SSH:
Параметр
Описание
PASS
Действие правила инспектирования SSH:
— Расшифровать.
PASS
— Не расшифровывать
enabled
Включение/отключение правила:
enabled(yes)
или
enabled(true)
enabled(no)
или
enabled(false)
name
Название правила инспектирования SSH.
Для указания названия правила:
name("SSH inspection rule example")
desc
Описание правила.
Например:
desc("SSH inspection rule example configured in CLI")
rule_log
Запись в журнал информации о трафике при срабатывании правила. Возможны варианты:
rule_log(no)
или
rule_log(false)
— отключить журналирование. Если при создании правила
rule_log
не указано, функция журналирования отключена.
rule_log(yes)
или
rule_log(true)
— включить журналирование.
block_ssh_shell
Блокирование удалённого запуска shell (интерпретатора командной строки, оболочки). Доступно в правилах с действием
Расшифровать
block_ssh_shell(yes)
или
block_ssh_shell(true)
— включить блокировку.
block_ssh_shell(no)
или
block_ssh_shell(false)
-отключить блокировку.
block_ssh_exec
Блокирование удалённого выполнения по SSH. Доступно в правилах с действием
Расшифровать
block_ssh_exec(yes)
или
block_ssh_exec(true)
— включить блокировку.
block_ssh_exec(no)
или
block_ssh_exec(false)
— отключить блокировку.
ssh_command
Команда linux, которую требуется передать, в формате
ssh user
host 'command'
Например:
ssh_command("ssh root@192.168.1.1 reboot")
Редактирование команды SSH доступно в правилах с действием
Расшифровать
block_sftp
Блокирование соединения SFTP (Secure File Transfer Protocol). Доступно в правилах с действием
Расшифровать
block_sftp(yes)
или
block_sftp(true)
— включить блокировку соединения.
block_sftp(no)
или
block_sftp(false)
— отключить блокировку соединения.
user
Пользователи и группы пользователей, для которых применяется правило инспектирования SSH (локальные или LDAP).
Для добавления LDAP групп и пользователей необходим корректно настроенный LDAP-коннектор (о настройке LDAP-коннектора через CLI читайте в разделе
Настройка LDAP-коннектора
Примеры добавления пользователей в правило:
user = known
user = "user"
user = "testd.local\\user1"
user = ("user", "testd.local\\user1")
src.zone
Зона источника трафика.
Для указания зоны источника, например, Trusted:
src.zone = Trusted
Подробнее о настройке зон с использованием интерфейса командной строки читайте в разделе
Зоны
src.ip
Добавление списков IP-адресов или доменов источника.
Для указания списка IP-адресов:
src.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI читайте в разделе
Настройка IP-адресов
Для указания списка доменов источника:
src.ip = lib.url()
; в скобках необходимо указать название URL, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки читайте в разделе
Настройка списков URL
src.geoip
Указание GeoIP источника; необходимо указать код страны (например,
src.geoip = RU
Коды названий стран доступны по ссылке
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15.
dst.ip
Добавление списков IP-адресов или доменов назначения.
Для указания списка IP-адресов:
dst.ip = lib.network()
; в скобках необходимо указать название списка. Подробнее о создании и настройке списков IP-адресов с использованием CLI читайте в разделе
Настройка IP-адресов
Для указания списка доменов назначения:
dst.ip = lib.url()
; в скобках необходимо указать название URL-списка, в который были добавлены необходимые домены. Подробнее о создании и настройке списков URL с использованием интерфейса командной строки читайте в разделе
Настройка списков URL
dst.geoip
Указание GeoIP назначения; необходимо указать код страны (например,
dst.geoip
= RU
Коды названий стран доступны по ссылке
ISO 3166-1
Важно!
Существует ограничение на количество GeoIP, которое может быть указано: не более 15.
service
Тип сервиса. Можно указать сервис или группу сервисов (подробнее читайте в разделах
Настройка сервисов
Настройка групп сервисов
Чтобы указать сервис:
service = "service name"
; для указания нескольких сервисов:
service = (service-name1, service-name2, ...)
Чтобы указать группу сервисов:
service = lib.service()
; в скобках необходимо указать название группы сервисов.
time
Настройка расписания работы правила.
Для установки расписания:
time = lib.time()
; в скобках необходимо указать название группы календарей.
Для редактирования правил инспектирования SSH используется команда:
Admin@nodename# set security-policy ssh-inspection <position> upl-rule
Для просмотра всех созданных правил инспектирования SSH используется команда:
Admin@nodename# show security-policy ssh-inspection
Для просмотра определенного правила инспектирования SSH используется команда:
Admin@nodename# show security-policy ssh-inspection <position>
Пример создания правила инспектирования SSH с использованием UPL:
Admin@nodename# create security-policy ssh-inspection 1 upl-rule OK \
...service = ("Any TCP") \
...block_ssh_shell(yes) \
...block_sftp(yes) \
...rule_log(yes) \
...name("Test SSH inspection rule") \
...desc("Test SSH inspection rule description") \
...enabled(true)
...
Admin@nodename# show security-policy ssh-inspection 1
% ----------------- 1 -----------------
OK \
service = "Any TCP" \
block_ssh_shell(yes) \
block_sftp(yes) \
desc("Test SSH inspection rule description") \
rule_log(yes) \
enabled(true) \
id(d703f390-896f-47c2-91bd-69c6d37aa6d2) \
name("Test SSH inspection rule")
Для удаления правила инспектирования SSH используется правило:
Admin@nodename# delete security-policy ssh-inspection <position>
v7.x
Настройка инспектирования SSL
Настройка СОВ

## Источник

https://docs.usergate.com/nastrojka-inspektirovaniya-ssh_826.html
