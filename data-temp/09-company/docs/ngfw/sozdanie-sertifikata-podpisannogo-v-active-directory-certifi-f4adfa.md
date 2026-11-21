---
заголовок: Создание сертификата, подписанного в Active Directory Certification Authority
url: https://docs.usergate.com/sozdanie-sertifikata-podpisannogo-v-active-directory-certification-authority_74.html
источник: портал документации
получено: 2026-11-20 16:15 +0700
продукт: NGFW
версия: 6.1.8, 6.1.9, 5.x
раздел: Создание сертификата, подписанного в Active Directory Certification Authority
id_статьи: 74
обновлено: 01 Nov, 2022
ревизия: 4
---

# Создание сертификата, подписанного в Active Directory Certification Authority

KnowledgeBase:
Для создания сертификата перейдите в раздел
UserGate ➜ Сертификаты
и выберите
Создать ➜ Новый CSR
. Заполните необходимые данные. В поле
Common name
укажите домен, который вы используете.
Выделите файл запроса и, нажав
Экспорт ➜ Экспорт CSR
, скачайте файл.
В Microsoft CA необходимо создать сертификат на основе полученного на предыдущем шаге CSR-файла. Для этого используется утилита certreq:
сertreq.exe -submit –attrib "CertificateTemplate:SubCA" .\certificate_csr.pem
где certificate_csr.pem - файл, созданный в консоли UserGate.
Далее необходимо выбрать центр сертификации.
Файл будет создан в формате PEM – PKCS#7.
В консоли UserGate выберите созданный ранее CSR и нажмите кнопку
Редактировать
. Загрузите файл сертификата и сохраните изменения.
Установите роль сертификата
SSL инспектирование
Также возможно использование web-приложения центра сертификации Microsoft Active Directory.
Тип сертификата может быть любой –
DER
или
PEM
В веб-консоли Microsoft CA выберите и скачайте сертификаты (публичные ключи) для самого Удостоверяющего Центра:
Импортируйте сертификаты в UserGate.
v5.x
v6.x
Создание сертификатов с помощью программы OpenSSL
Создание сертификатов с помощью программы XCA

## Источник

https://docs.usergate.com/sozdanie-sertifikata-podpisannogo-v-active-directory-certification-authority_74.html
