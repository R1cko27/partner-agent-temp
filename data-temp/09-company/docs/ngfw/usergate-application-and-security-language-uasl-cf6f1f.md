---
заголовок: UserGate Application and Security Language (UASL)
url: https://docs.usergate.com/usergate-application-and-security-language-(uasl)_885.html
получено: 2026-11-20 16:14 +0700
продукт: NGFW
версия: 7.x
раздел: UserGate Application and Security Language (UASL)
id_статьи: 885
обновлено: 12 Mar, 2025
ревизия: 6
---

# UserGate Application and Security Language (UASL)

Documentation:
Общие положения
UserGate Application and Security Language (UASL) – язык, разработанный для возможности написания пользовательских сигнатур и приложений.
После создания пользовательские сигнатуры и приложения можно добавлять в профили СОВ и приложений для дальнейшего использования в правилах межсетевого экранирования.
Структура сигнатуры выглядит следующим образом:
UASL (.parameter1=<value1>; .parameter2=<value2>; …)
Параметры сигнатуры записываются в круглых скобках; для разделения параметров используется точка с запятой (;).
Также допускается использование многострочного ввода:
UASL (.parameter1=<value1>;
.parameter2=<value2>;
...
Примечание
Максимальная длина пользовательской сигнатуры составляет 1024 байта.
Все условия одной сигнатуры без исключений будут объединены логическим оператором
Создание, редактирование или удаление сигнатур можно отслеживать по записям журнала событий.
Подробнее о семантике, конструкциях и правилах языка UASL читайте в следующих статьях данного раздела.
v7.x
UserGate Application and Security Language (UASL)
Метаинформация

## Источник

https://docs.usergate.com/usergate-application-and-security-language-(uasl)_885.html
