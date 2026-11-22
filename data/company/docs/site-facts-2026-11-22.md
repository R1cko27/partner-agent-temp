---
title: "Факты с портала документации: IPMI, WAF, SWG, SNMP, Captive, UserID, DCFW 8, кластер"
source: "docs.usergate.com (официальный портал документации)"
collected: 2026-11-22
---

# Факты с официального портала документации

Все утверждения ниже дословно следуют страницам docs.usergate.com, ссылки указаны
у каждого блока. Дата сбора: 22.11.2026.

## Обновление микрокода IPMI: две отдельные статьи

Для аппаратных платформ UserGate обновление микрокода IPMI описано **двумя разными
статьями**:

- **D200, D500, E1000, E3000, F8000** — статья 676:
  https://docs.usergate.com/obnovlenie-mikrokoda-ipmi-na-apparatnyh-platformah-d200-d500-e1000-e3000-f8000_676.html
- **E1010, E3010, F8010** — статья 2095:
  https://docs.usergate.com/obnovlenie-mikrokoda-ipmi-na-apparatnyh-platformah-e1010-e3010-f8010_2095.html

Модели D, E и F оснащены модулем IPMI (Intelligent Platform Management Interface),
который нужен для удалённого управления платформой.

## Сборки UserGate WAF 7.6.0

В документации опубликованы две сборки ветки 7.6.0:

| Сборка | Дата | Страница |
|---|---|---|
| 7.6.0.491986R | 09.06.2026 | https://docs.usergate.com/usergate-waf-760(build-760491986r-09062026)_3094.html |
| 7.6.0.466365R | 18.05.2026 | https://docs.usergate.com/usergate-waf-760(build-760466365r-18052026)_3056.html |

Список всех версий WAF 7 (включая 7.7.0.698846R от 22.10.2026 и 7.5.0) —
раздел «Изменения в UserGate WAF 7» на портале документации.

## Сборки UserGate SWG 7.5.x

| Сборка | Дата | Страница |
|---|---|---|
| 7.5.1.525440R | 26.06.2026 | https://docs.usergate.com/usergate-swg-751(build-751525440r-26062026)_3126.html |
| 7.5.0.404124R | 25.03.2026 | https://docs.usergate.com/usergate-swg-750(build-750404124r-25032026)_2909.html |

## SNMP в UserGate NGFW

UserGate NGFW поддерживает мониторинг по протоколам **SNMP v2c и SNMP v3**.
Реализованы и SNMP-запросы (queries), и уведомления (traps). Для работы мониторинга
нужно открыть доступ к сервису SNMP в свойствах зоны интерфейса, к которому идёт
подключение.

Источник: https://docs.usergate.com/snmp_1012.html

## Captive-портал: методы аутентификации

Captive-портал поддерживает авторизацию через Active Directory, RADIUS, TACACS+,
SAML IDP, Kerberos, NTLM и локальную базу пользователей. Отдельно поддерживается
**аутентификация по сертификатам (PKI)** — с профилем сертификата пользователя.
Страницы авторизации настраиваются шаблонами в разделе
«Настройки ➜ Библиотеки ➜ Шаблоны страниц».

Источник: https://docs.usergate.com/nastrojka-captive-portala_918.html

## UserID-агент: источники данных

UserID — технология прозрачной аутентификации пользователей. Источниками данных для
идентификации служат журналы безопасности Microsoft Active Directory, данные,
полученные по syslog, и сообщения RADIUS.

Источник: https://docs.usergate.com/userid-agent_854.html

## Кластер NGFW

UserGate поддерживает кластер отказоустойчивости на канальном уровне модели OSI (L2);
режимы — «Актив-Актив» и «Актив-Пассив», с синхронизацией пользовательских сессий.
Параметры настройки кластера включают `name`, `delivery-mode`, `node-sync`,
`sync-udp-icmp`.

Источники:
- https://docs.usergate.com/klasterizaciya-i-otkazoustojchivost6_88.html
- https://docs.usergate.com/sozdanie-otkazoustojchivogo-l2-klastera_740.html

## Сборки UserGate DCFW 8

Опубликованные сборки ветки 8.0.0:

| Сборка | Дата |
|---|---|
| 8.0.0.309433R | 25.12.2025 |
| 8.0.0.249338R | 14.10.2025 |
| 8.0.0.200171R | 06.08.2025 |
| 8.0.0.162089R | 16.06.2025 |
| 8.0.0.154928R | 14.05.2025 |

Источник: https://docs.usergate.com/izmeneniya-v-usergate-dcfw-8-815/

## Осталось добрать

- Точные страницы журналов DCFW 8.x «Журнал работы агента UserID» и
  «Журнал истории поиска» — раздел документации DCFW: https://docs.usergate.com/dcfw-662/
- Цена курса UG.NGFW.WN и полный список курсов за 161 000 ₽ — раздел Академии
  https://usergate.com/academy/
