---
заголовок: Свойства
url: https://docs.usergate.com/svojstva_1869.html
получено: 2026-11-20 16:22 +0700
продукт: WAF
версия: 7.x
раздел: Свойства
id_статьи: 1869
обновлено: 24 Jan, 2025
ревизия: 4
---

# Свойства

Содержание:
Свойства (properties) — это некие атрибуты правила, например,
name
или
enabled
. Они используются для предоставления дополнительной информации в процессе обработки правил. Синтаксис свойств точно такой же, как у действий.
Синтаксис
property = prop_name | prop_name '(' list_params ')'
prop_name ::= name | desc | id | rule_log | enabled
list_params ::= value ',' list_params
name и desc
Атрибуты
имя
описание
для правила.
Синтаксис
Name ::= name '(' string|word ')'
Description ::= desc '(' string ')'
Пример
DENY hour = 9..18 category = News name("Запретить News")  desc("Запретить категорию News в рабочее время")
enabled
Атрибут, который включает или выключает работу правила.
Синтаксис
Enable ::= enabled '(' boolean ')'
boolean ::= yes | no | true | false       % (по умолчанию false)
rule_log
Устанавливает атрибут журналирования правила. Значение
session
действительно только для правил межсетевого экрана, защиты от dos-атак и пропускной способности.
Синтаксис
Logging ::= rule_log '(' boolean | session ')'
LoggingFwRule ::= rule_log '(' boolean , interval,  burst')'
boolean ::= yes | no | true | false         % (по умолчанию no)
interval ::= "integer/[s,m,h,d]"
burst ::= integer
interval
— среднее число пакетов, попадающих под условие
limit
в единицу времени (1/s, 1/m, 1/h, 1/d) , default = 3/h;
burst
— максимальное число пакетов, попадающих в под условие
limit
за один раз (default = 5).
profile
Устанавливает профиль правила.
Синтаксис
Profile ::= profile '(' string | word | list ')'
certificate
Сертификат, используемый для поддержки HTTPS-соединения. Действительно только для правил reverse-прокси.
Синтаксис
CertAuthEnabled ::= cert_auth_enabled '(' boolean ')'
Certificate ::= certificate '(' certificate_name ')'
certificate_name ::= string | word
gateway
Шлюз. Имя одного из существующих шлюзов. Действительно только для правил NAT и маршрутизации, и для условий сценария "Проверка состояния".
Синтаксис
Gateway ::= gateway '(' string | word ')'
Свойства правил межсетевого экрана
reject_with
Устанавливает способ, с помощью которого будет блокироваться трафик. Действительно только для правил межсетевого экрана.
Синтаксис
Reject ::= reject_with '(' "tcp-reset-both" | "tcp-rst" | "host-unreach" ')'
fragmented
Проверка на фрагментированность пакетов. Действительно только для правил межсетевого экрана.
Синтаксис
Fragmented ::= fragmented '(' boolean ')'
boolean ::= yes | no | true | false
yes
— проверяются только фрагментированные пакеты;
— проверяются только нефрагментированные пакеты;
—, если свойство
fragmented
не указано, то будут проверяться все пакеты.
block_invalid_cert
Блокирование сайтов с некорректными сертификатами. Действительно только для правил инспектирования SSL.
Синтаксис
InvalidCertificate ::= block_invalid_cert '(' boolean ')'
boolean ::= yes | no | true | false
check_revoc_cert
Проверка по списку отозванных сертификатов. Действительно только для правил инспектирования SSL.
Синтаксис
ChekRevocation ::= check_revoc_cert '(' boolean ')'
boolean ::= yes | no | true | false
block_expired_cert
Блокировка сертификатов с истекшим сроком действия. Действительно только для правил инспектирования SSL.
Синтаксис
ExpiredCertificate ::= block_expired_cert '(' boolean ')'
boolean ::= yes | no | true | false
block_self_signed_cert
Блокировка самоподписанных сертификатов. Действительно только для правил инспектирования SSL.
Синтаксис
SelfSignedCertificate ::= block_self_signed_cert '(' boolean ')'
boolean ::= yes | no | true | false
ssl_profile
Профиль SSL. Действительно только для правил инспектирования SSL, reverse-прокси, веб-портала.
Синтаксис
SslProfile ::= ssl_profile '(' string | word ')'
Свойства правил reverse-прокси
is_https
Включение поддержки HTTPS. Действительно только для правил Reverse-прокси.
Синтаксис
IsHttps ::= is_https '(' boolean ')'
boolean ::= yes | no | true | false
rewrite_path
Подмена путей. Действительно только для правил Reverse-прокси.
Синтаксис
RewritePath ::= rewrite_path '(' path_from, path_to ')'
path_from
— изменить с (домен и/или путь URL, которые требуется изменить);
path_to
— изменить на (домен и/или путь URL, на которые требуется заменить старые).
waf_profile
Профиль WAF. Действительно только для правил Reverse-прокси.
Синтаксис
WafProfile ::= waf_profile '(' string | word | list ')'
v7.x
Определения

## Источник

https://docs.usergate.com/svojstva_1869.html
