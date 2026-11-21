---
заголовок: Управление областями
url: https://docs.usergate.com/upravlenie-oblastyami-490/
источник: портал документации
получено: 2026-11-20 16:31 +0700
продукт: Management Center
версия: 7.x
раздел: Интерфейс командной строки
крошки: Главная / Документация / Management Center / Management Center 7.x Руководство администратора / Интерфейс командной строки / Управление областями
---

# Управление областями

Настройка управляемых областей
Для возможности управление областями администратор UGMC должен выполнить следующие действия:
Создать область.
Создать профиль администратора с типом администратора области.
Создать администратора области.
Подробнее об управлении областями в UGMC читайте в разделе
Управление областями
Создание управляемой области
Настройка управляемых областей производится на уровне
realms
Для создания управляемой области используется команда:
Admin/system@nodename# create realm <parameters>
Далее необходимо указать следующие параметры:
Параметр
Описание
name
Название управляемой области.
description
Описание управляемой области.
code-name
Код области. Состоит из нескольких букв и/или цифр. Код области необходимо указывать при входе в консоль для управления данной областью. Например, UG.
is-default
Область по умолчанию. Если данная опция установлена, то при аутентификации в консоль необязательно указывать имя области через слэш.
max-devices
Максимальное количество управляемых устройств UserGate NGFW в области.
max-ep-devices
Максимальное количество управляемых конечных устройств (UserGate Client) в области.
Пример создания управляемой области:
Admin/system@nodename# create realms name "Test realm" code-name tstrlm1 is-default on max-devices 10 max-ep-devices 100
Пример команды для просмотра имеющихся управляемых  областей:
Admin/system@nodename# show realms
Example realm
name              : Example realm
is-default        : off
description       : Example realm created for demo purpose. Can be changed or deleted if necessary.
code-name         : EX
num-devices       : 1
num-ep-devices    : 0
max-devices       : unlimited
max-ep-devices    : unlimited
Test realm
name              : Test realm
is-default        : on
code-name         : tstrlm1
num-devices       : 0
num-ep-devices    : 0
max-devices       : 10
max-ep-devices    : 100
Пример команды для редактирования параметров созданных ранее управляемых областей:
Admin/system@nodename# set realms "Test realm" max-devices 50
Admin/system@nodename# show realms "Test realm"
name              : Test realm
is-default        : off
code-name         : tstrlm1
num-devices       : 0
num-ep-devices    : 0
max-devices       : 50
max-ep-devices    : 100
Пример команды удаления созданной ранее управляемой области:
Admin/system@nodename# delete realms "Test realm"
Создание администратора управляемой области
Для управления созданной ранее областью необходимо создать администратора области.
Профиль администратора с типом администратора области создается, как описано в разделе
Настройка прав доступа профилей администраторов
Учетная запись администратора области создаются, как описано в разделе
Настройка учетных записей администраторов
Просмотреть как статью
к началу

## Источник

https://docs.usergate.com/upravlenie-oblastyami-490/
