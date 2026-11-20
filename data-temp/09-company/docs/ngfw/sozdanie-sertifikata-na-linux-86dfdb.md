---
заголовок: Создание сертификата на Linux
url: https://docs.usergate.com/sozdanie-sertifikata-na-linux_385.html
источник: портал документации
получено: 2026-11-20 16:14 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9, 5.x
раздел: Создание сертификата на Linux
id_статьи: 385
обновлено: 01 Nov, 2022
ревизия: 4
---

# Создание сертификата на Linux

KnowledgeBase:
Создать пользовательский сертификат. Скачать файл
generate-auth-certificate.sh
. В данном файле содержится скрипт для создания SSL-сертификата.
Через терминал войти в папку, где сохранён файл и выполнить следующую команду:
sh generate-auth-certificate.sh
После выполнения будет создана папка auth-certiifcates.
С использованием команды ls –l можно вывести список всех файлов любой директории, включая скрытые.
ls -l ./auth-certificates
итого 16
-rw------- 1 emv emv 3882 янв 20 11:21 Admin.p12
drwxr-xr-x 2 root root 4096 янв 20 11:21 basefiles
-rw-r--r-- 1 root root 1229 янв 20 11:21 ca.crt
-rw------- 1 root root 3896 янв 20 11:21 NotAdmin.p12
Просмотрим содержимое папки auth-certiifcates/basefiles:
ls –l ./auth-certificates/basefiles
итого 20
-rw-r--r-- 1 root root 1460 янв 20 11:21 Admin.crt
-rw------- 1 root root 3243 янв 20 11:21 Admin.key
-rw------- 1 root root 1675 янв 20 11:21 ca.key
-rw-r--r-- 1 root root 1464 янв 20 11:21 NotAdmin.crt
-rw------- 1 root root 3243 янв 20 11:21 NotAdmin.key
Далее можно выполнять импорт сертификатов.
v5.x
v6.x
v7.x
Создание сертификатов с помощью программы XCA
Создание сертификата на Windows

## Источник

https://docs.usergate.com/sozdanie-sertifikata-na-linux_385.html
