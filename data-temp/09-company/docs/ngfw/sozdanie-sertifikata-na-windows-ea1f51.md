---
заголовок: Создание сертификата на Windows
url: https://docs.usergate.com/sozdanie-sertifikata-na-windows_390.html
источник: портал документации
получено: 2026-11-20 16:14 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9, 5.x
раздел: Создание сертификата на Windows
id_статьи: 390
обновлено: 01 Nov, 2022
ревизия: 3
---

# Создание сертификата на Windows

KnowledgeBase:
Для создания сертификата будет использоваться библиотека OpenSSL. После установки OpenSSL на Windows создать 2 папки: auth-certificates и basefiles в папке auth-certificates.
Открыть командную строку в режиме администратора и зайти в ранее созданную папку auth-certificates.
С использованием следующих команд создать Х.509-сертификат:
openssl req -x509 -newkey rsa:2048 -keyout basefiles/ca.key -nodes -out ca.crt -subj '/CN=Entensys Auth CA/L=Novosibirsk/C=RU'
openssl rsa -in basefiles/ca.key -out basefiles/ca.key
В файле ca-key.pem будет находиться приватный ключ сертификата, в ca.pem - публичный ключ.
Далее необходимо создать приватные RSA ключи и сгенерировать самоподписанные сертификаты Admin.crt и NotAdmin.crt:
openssl genrsa -out basefiles/Admin.key 4096
openssl req -new -key basefiles/Admin.key -out $TMP_FILE -subj '/CN=Admin/L=Novosibirsk/C=RU/O=Entensys/OU=Unit1'
openssl x509 -req -days 365 -CA ca.crt -CAkey basefiles/ca.key -set_serial 01 -in $TMP_FILE -out basefiles/Admin.crt
openssl pkcs12 -password pass:1234 -export -out Admin.p12 -name "UTM user Admin" -in basefiles/Admin.crt -inkey basefiles/Admin.key
openssl genrsa -out basefiles/NotAdmin.key 4096openssl req -new -key basefiles/NotAdmin.key -out $TMP_FILE -subj '/CN=NotAdmin/L=Novosibirsk/C=RU/O=Entensys/OU=Unit2'
openssl x509 -req -days 365 -CA ca.crt -CAkey basefiles/ca.key -set_serial 02 -in $TMP_FILE -out basefiles/NotAdmin.crtopenssl pkcs12 -password pass:1234 -export -out NotAdmin.p12 -name "UTM user NotAdmin" -in basefiles/NotAdmin.crt -inkey basefiles/NotAdmin.keyrm -f $TMP_FILE
Далее можно выполнять импорт сертификатов.
v5.x
v6.x
Создание сертификата на Linux
Распространение сертификатов UserGate на клиентские компьютеры с...

## Источник

https://docs.usergate.com/sozdanie-sertifikata-na-windows_390.html
