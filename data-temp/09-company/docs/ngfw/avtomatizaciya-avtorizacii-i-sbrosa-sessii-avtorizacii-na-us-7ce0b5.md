---
заголовок: Автоматизация авторизации и сброса сессии авторизации на UserGate для доменного пользователя
url: https://docs.usergate.com/avtomatizaciya-avtorizacii-i-sbrosa-sessii-avtorizacii-na-usergate-dlya-domennogo-pol6zovatelya_202.html
получено: 2026-11-20 16:13 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9
раздел: Автоматизация авторизации и сброса сессии авторизации на UserGate для доменного пользователя
id_статьи: 202
обновлено: 20 Sep, 2023
ревизия: 14
---

# Автоматизация авторизации и сброса сессии авторизации на UserGate для доменного пользователя

Содержание:
KnowledgeBase:
Windows
При использовании прозрачной авторизации пользователей по протоколу Kerberos существует возможность автоматизировать авторизацию пользователей на captive-портале UserGate в момент их авторизации на ПК и сброс авторизации на UserGate в момент завершения их сессии на ПК. Для этого используется штатные механизм logon и logoff скриптов Windows(см. п.
Автоматическая регистрация пользователя на UserGate UTM посредством REST API
) и механизм Group Policy домена Active Directory (см. документацию Microsoft). В качестве скрипта автоматической авторизации предлагается следующий вариант скрипта PowerShell:
$Response = Invoke-WebRequest -Uri http://detectportal.firefox.com/ -Proxy 'http://auth.trusted.com:8090' -ProxyUseDefaultCredentials
Write-Host $Response.StatusDescription
где auth.trusted.com - домен Auth captive-портала, настроенный на UserGate в разделе UserGate ➜Настройки ➜ Модули. http://detectportal.firefox.com/ - любой доверенный, гарантированно доступный Интернет-ресурс, предпочтительно HTTP, а не HTTPS. В качестве скрипта автоматического сброса сессии авторизованного на UserGate пользователя предлагается следующий вариант скрипта PowerShell:
$Session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$Cookie = New-Object System.Net.Cookie
$Cookie.Name = 'csrf_token'
$Cookie.Value = 'foo'
$Cookie.Domain = 'logout.trusted.com'
$Session.Cookies.Add($Cookie);
$Body = @{
csrfmiddlewaretoken = 'foo'
$Response = Invoke-WebRequest -Uri http://logout.trusted.com:8002/cpa/logout -Method POST -Body $Body -WebSession $Session
Write-Host $Response.StatusDescription
где logout.trusted.com - домен Logout captive-портала, указанный на UserGate в разделе UserGate ➜Настройки ➜ Модули.
Примечание
В случае, когда доменными политиками определено использование нескольких logon/logoff скриптов, рекомендуется указанный logoff-скрипт использовать последним, а logon-скрипт - ближе к началу списка.
Linux
Для использования прозрачной авторизации на ОС семейства Linux, подойдет следующая команда
curl --proxy-negotiate -u:user -x auth.usergate.demo:8090 http://cbr.ru &> /dev/null
Где
-u:user - Буквально. Не нужно подставлять имя какого-то конкретного пользователя.
auth.usergate.demo - FQDN вашего проки сервера UserGate
http://cbr.ru - Любой url. Его цель лишь в заполнении соответсвующего поля при формировании web запроса к прокси-серверу.
Для осуществления сброса авторизации, можно использовать команду
curl --cookie "csrf_token=foo" -v -X POST -d "csrfmiddlewaretoken=foo" -H "Content-Type: application/x-www-form-urlencoded" http://logout.usergate.demo:8002/cpa/logout
Где logout.usergate.demo - FQDN вашего проки сервера UserGate
Примечание
Команда должна выполняться с того же адреса, на котором работает уже авторизоавнный пользователь и сессию которого надо прекратить.
Примечание
Пользовательский компьютер с ОС Linux доолжен быть настроен на взаимодействие и авторизацию пользователя с помощью домена.
Данные команды можно запустить штатными средствами ОС:
С помощью xprofile
В домашней директории пользователя создайте файл
xprofile
(точка обязательна) и сделайте файл исполняемым (chmod +x ~/.xprofile).
Далее, пропишите в файле следующие строки:
#!/bin/bash
/path-to-curl/curl --proxy-negotiate -u:user -x auth.usergate.demo:8090 http://cbr.ru &> /dev/null
trap '. /path-to-curl/curl --cookie "csrf_token=foo" -v -X POST -d "csrfmiddlewaretoken=foo" -H "Content-Type: application/x-www-form-urlencoded" http://logout.usergate.demo:8002/cpa/logout; exit' 0
С помощью system.d
В этом случае необходимо создать файл сервиса и зарегистрировать его в
systemd
Для этого создайте файл с произвольным именем, например,
auth
service
в каталоге
~/.config/systemd/user
Добавьте в файл следующее:
Description=Auth service on UserGate UTM
After=network.target network-online.target
Wants=network-online.target
Type=oneshot
RemainAfterExit=true
TimeoutStartSec=0
ExecStart=/path-to-curl/curl --proxy-negotiate -u:user -x auth.usergate.demo:8090 http://cbr.ru > /dev/null
ExecStop=/path-to-curl/curl --cookie "csrf_token=foo" -v -X POST -d "csrfmiddlewaretoken=foo" -H "Content-Type: application/x-www-form-urlencoded" http://logout.usergate.demo:8002/cpa/logout
WantedBy=default.target
Выполните команды (вместо
auth
service
укажите название файла, созданного на шаге 1):
systemctl --user daemon-reload
systemctl --user enable
auth.service
v6.x
v7.x
Также опубликовано в
Документация -> Общие сведения -> Взаимодействие со сторонними решениями
Установка и настройка агента терминального сервера UserGate
Авторизация с помощью NTLM

## Источник

https://docs.usergate.com/avtomatizaciya-avtorizacii-i-sbrosa-sessii-avtorizacii-na-usergate-dlya-domennogo-pol6zovatelya_202.html
