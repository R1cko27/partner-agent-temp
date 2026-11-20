---
заголовок: Создание сертификатов с помощью программы OpenSSL
url: https://docs.usergate.com/sozdanie-sertifikatov-s-pomosh6yu-programmy-openssl_70.html
получено: 2026-11-20 16:14 +0700
продукт: NGFW
версия: 5.x, 6.1.8, 6.1.9
раздел: Создание сертификатов с помощью программы OpenSSL
id_статьи: 70
обновлено: 24 May, 2024
ревизия: 14
---

# Создание сертификатов с помощью программы OpenSSL

KnowledgeBase:
Выбрать каталог для хранения ключей и сертификатов и назначить необходимый уровень доступа.
# mkdir /root/ca
# cd /root/ca
# mkdir certs crl newcerts private # chmod 700 private # touch index.txt
Сгенерировать приватный ключ.
# openssl genrsa -out /root/ca/private/ca_key.pem 2048
Создать сертификат CA для этого приватного ключа.
# openssl req -new -x509 -days 3650 -key /root/ca/private/ca_key.pem -out /root/ca/certs/ca.crt
Вывод команды:
You are about to be asked to enter information that will be incorporated into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
Country Name (2 letter code) [AU]:RU
State or Province Name (full name) [Some-State]:NSO
Locality Name (eg, city) []:Novosibirsk
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Kraftec
Organizational Unit Name (eg, section) []: Common Name (e.g. server FQDN or YOUR name) []:www.kraftec.net Email Address [`]:dit@kraftec.net
Создать конфигурационный файл для OpenSSL.
Для создания сертификата SSL для Captive портала и Веб-консоли необходимо создать файл конфигурации.
# touch /root/ca/openssl.cnf
Добавьте в данный файл следующие блоки:
Примечание
Для получения одного сертификата для всех узлов кластера
subjectAltName
(Subject Alternative Name, SAN) не указывается в запросе на сертификат; все SAN указываются при подписании запроса в УЦ.
[ ca ]
default_ca = CA_default
[ CA_default ]
dir = /root/ca
certs = $dir/certs
crl_dir = $dir/crl
database = $dir/index.txt
new_certs_dir = $dir/newcerts
certificate = $certs/ca.crt
private_key = $dir/private/ca_key.pem
serial = $dir/serial
crlnumber = $dir/crlnumber
crl = $dir/crl/crl.pem
RANDFILE = $dir/private/.rand
x509_extensions = usr_cert
name_opt = ca_default
cert_opt = ca_default
crl_extensions = crl_ext
default_days = 365
default_crl_days= 30
default_md = sha256
preserve = no
policy = policy_match
[ policy_match ]
countryName = match
stateOrProvinceName = match
organizationName = match
organizationalUnitName = optional
commonName = supplied
emailAddress = optional
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
string_mask = utf8only
[ req_distinguished_name ]
countryName = Country Name (2 letter code)
countryName_default = RU
countryName_min = 2
countryName_max = 2
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default = NSO
localityName = Locality Name (eg, city)
localityName_default = Novosibirsk
0.organizationName = Organization Name (eg, company)
0.organizationName_default = Kraftec
organizationalUnitName = Organizational Unit Name (eg, section)
#organizationalUnitName_default =
commonName = Common Name (e.g. server FQDN or YOUR name)
commonName_max = 64
emailAddress = Email Address
emailAddress_max = 64
[ usr_cert ]
basicConstraints=CA:FALSE
nsCertType = server
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
subjectAltName=DNS:auth.kraftec.net, DNS:logout.kraftec.net,DNS:block.kraftec.net, DNS:ftpclient.kraftec.net, DNS:sslvpn.kraftec.net
[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = critical,CA:true
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
[ crl_ext ]
authorityKeyIdentifier=keyid:always
Сгенерировать ключ для SSL-сертификата Captive-портала.
# openssl genrsa -out /root/ca/private/Captive_key.pem 2048
Сгенерировать ключ для SSL-сертификата Веб-консоли
# openssl genrsa -out /root/ca/private/Web_key.pem 2048
Сгенерировать запрос на SSL-сертификат Captive-портала
# openssl req -new -key /root/ca/private/Captive_key.pem -config /root/ca/openssl.cnf -out /root/ca/Captive.csr
Вывод команды:
You are about to be asked to enter information that will be incorporated into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
Country Name (2 letter code) [RU]:
State or Province Name (full name) [NSO]:
Locality Name (eg, city) [Novosibirsk]:
Organization Name (eg, company) [Kraftec]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:auth.kraftec.net
Email Address []: dit@kraftec.net
Подписать полученный запрос с помощью сертификата УЦ.
# openssl x509 -req -days 365 -CA /root/ca/certs/ca.crt -CAkey /root/ca/private/ca_key.pem -extfile /root/ca/openssl.cnf -extensions usr_cert -in Captive.csr -out Captive.crt
Вывод команды:
Signature ok>
subject=/C=RU/ST=NSO/L=Novosibirsk/O=Kraftec/CN=auth.kraftec.net/emailAddress=dit@kraftec.net
Getting CA Private Key
Сгенерировать запрос на SSL-сертификат Веб-консоли.
Предварительно исправьте конфигурационный файл usr_cert: измените параметр на
subjectAltName=DNS:utm.kraftec.net
# openssl req -new -key /root/ca/private/Web_key.pem -config /root/ca/openssl.cnf -out /root/ca/Web.csr
Вывод команды:
You are about to be asked to enter information that will be incorporated> into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
Country Name (2 letter code) [RU]:
State or Province Name (full name) [NSO]:
Locality Name (eg, city) [Novosibirsk]:
Organization Name (eg, company) [Kraftec]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:utm.kraftec.net
Email Address []: dit@kraftec.net
Подписать полученные запросы с помощью сертификата УЦ.
# openssl x509 -req -days 365 -CA /root/ca/certs/ca.crt -CAkey /root/ca/private/ca_key.pem -extfile /root/ca/openssl.cnf -extensions usr_cert -in Web.csr -out Web.crt
Вывод команды:
Signature ok
subject=/C=RU/ST=NSO/L=Novosibirsk/O=Kraftec/CN=utm.kraftec.net/emailAddress=dit@kraftec.net
Getting CA Private Key
Импортировать данные сертификаты и приватные ключи в UserGate в разделе
UserGate ➜ Сертификаты
Назначьте сертификатам следующие роли:
Сертификату ca.crt:
SSL дешифрование
Сертификату Captive.crt:
SSL captive-портала
Сертификату Web.crt:
SSL веб-консоли
Установите сертификат ca.crt на компьютеры пользователей в хранилище
Доверенные корневые центры сертификации
v5.x
v6.x
v7.x
Сертификаты
Создание сертификата, подписанного в Active Directory...

## Источник

https://docs.usergate.com/sozdanie-sertifikatov-s-pomosh6yu-programmy-openssl_70.html
