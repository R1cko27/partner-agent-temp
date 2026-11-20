---
заголовок: Настройка браузера Chrome на Linux для авторизации Kerberos/Captive portal
url: https://docs.usergate.com/nastrojka-brauzera-chrome-na-linux-dlya-avtorizacii-kerberoscaptive-portal_69.html
получено: 2026-11-20 16:17 +0700
продукт: NGFW
раздел: Настройка браузера Chrome на Linux для авторизации Kerberos/Captive portal
id_статьи: 69
обновлено: 22 Mar, 2023
ревизия: 4
---

# Настройка браузера Chrome на Linux для авторизации Kerberos/Captive portal

Содержание:
Задача
В браузере Chrome (и его вариациях) не отображается портал авторизации. Пользователь видит пустое окно со следующим содержимым:
Заголовок:
HTTP/1.1 407 Authorization Required
Содержимое страницы
<html> <!-- please auth via kerberos/NTLM ➜ </html>
Решение
Для подробной информации по работе с политиками в браузере, обратитесь к документации по адресу:
https://www.chromium.org/administrators/linux-quick-start
В соответствии с инструкцией, нужно создать json-файл в директории managed:
touch /etc/opt/chrome/policies/managed/test_policy.json
Содержимое файла должно быть следующего вида:
"AuthServerWhitelist": "*.usergate.demo",
"AuthSchemes": "ntlm,negotiate"
“usergate.demo” необходимо заменить на доменное имя вашего домена.
В браузере Chrome открыть страницу политик
about:policy
Вы должны увидеть настройки прописанные в файле на открытой странице:
Если этих строк нет, значит браузеру не удалось загрузить политики из созданного файла. Проверьте права доступа, и другие возможные причины. Обратите внимание, различные браузеры имеют особенности в загрузке политик. Например браузер Chromium на Kali Linux автоматически не загружает описанные политики.
После проведенных манипуляций, браузер не способный произвести прозрачную Kerberos аутентификацию, будет перенаправлять пользователя на портал авторизации.
v5.x
Разрешения доступа администраторов
Некорректная работа правил UserGate NGFW при работе с доменными...

## Источник

https://docs.usergate.com/nastrojka-brauzera-chrome-na-linux-dlya-avtorizacii-kerberoscaptive-portal_69.html
