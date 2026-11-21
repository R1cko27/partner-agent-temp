---
заголовок: Пользовательская нормализация логов
url: https://docs.usergate.com/pol6zovatel6skaya-normalizaciya-logov_1967.html
источник: портал документации
получено: 2026-11-20 16:25 +0700
продукт: SIEM
версия: 7.x
раздел: Пользовательская нормализация логов
id_статьи: 1967
обновлено: 12 May, 2026
ревизия: 9
---

# Пользовательская нормализация логов

Documentation:
Technology: SIEM
Правила нормализации логов позволяют приводить к единому виду данные, полученные UserGate SIEM с различных источников (сенсоров).
Логи, поступающие с различных сенсоров в UserGate SIEM, могут обрабатываться с помощью регулярных выражений, указанных в правилах пользовательской нормализации. В результате данные, найденные в логах, будут записаны в стандартные поля базы данных UserGate SIEM.
Порядок выполнения правил нормализации задается администратором в разделе
Журналы и отчеты ➜ Журналы ➜ Пользовательская нормализация логов
. Последующие правила могут перезаписать значения, нормализованные и записанные предыдущими. Менять расположение правила можно перетаскиванием правила с помощью мыши, или с помощью кнопок меню:
Вниз
Наверх
Выше
Ниже
Источники логов и их поля, которые можно дополнительно нормализовать:
Журнал событий конечных устройств
Syslog
Конечное устройство (sensorName)
Правило (ruleName)
Данные (data)
Имя компьютера (computerName)
Статус (status)
Приложение (applicationName)
Источник журнала событий (sourceName)
Идентификатор процесса (processId)
Категория инцидента (logCategoryString)
Данные (data)
Имя компьютера (computerName)
Пользователь (userName)
Строка вставки (insertionString)
Файл журнала лога (logFile)
Список полей базы данных UserGate SIEM, в которые можно сохранять найденные данные (т.е. использовать эти названия полей в регулярных выражениях в правилах нормализации):
Название
Тип
node
string
userId
guid
user
string
ruleId
guid
rule
string
ipSource
ipDest
portSource
integer16
portDest
integer16
macSource
mac
macDest
mac
natIpSource
natIpDest
natPortSource
integer16
natPortDest
integer16
applicationName
string
bytesSent
integer64
bytesRecv
integer64
packetsSent
integer64
packetsRecv
integer64
mime
string
httpMethod
string
referer
url
statusCode
integer16
userAgent
string
sensor
string
sensorId
guid
processId
string
networkProtocol
ip protocol
status
string
error
integer
counterId
guid
logCategory
integer16
taskCategory
string
computerName
string
logEventCode
integer16
logEventId
integer16
logEventType
integer16
logFile
string
severity
module
string
component
string
event
string
syslogFacility
integer8
syslogSeverity
integer8
image
string
cmdLine
string
originalFileName
string
parentProcessId
integer64
parentImage
string
parentCommandLine
string
targetObject
string
targetFilename
string
scriptBlockText
string
queryName
string
queryResults
string
workstationName
string
logonId
string
imageLoaded
string
sourceImage
string
targetImage
string
customString1
string
...
string
customString15
string
customNumber1
string
...
string
customNumber5
string
customIp1
customIp2
customDate1
date
customDate2
date
Типы полей:
Тип
Значение по умолчанию
Описание
string
Строка любой длины.
guid
00000000-0000-0000-0000-00000000000
Строка вида XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX, где X - шестнадцатиричная цифра (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, a, b, c, d, e, f, A, B, C, D, E, F).
0.0.0.0
Строка вида X.X.X.X, где X = 0..255; или X:X:X:X:X:X:X:X, где X = 4-значное шестнадцатиричное число.
integer
0
Любое целое неотрицательное число.
url
Строка URL, формат в RFC1738.
ip protocol
255
Число 0 .. 255 или строка из
списка протоколов
ниже.
severity
unknown
Строки: unknown, critical, error, info, warning.
integer8
0
Целое число в интервале [0, 255].
integer16
0
Целое число в интервале [0, 65535].
integer64
0
Целое число в интервале [0, 2^64-1].
date
1970-01-01T00:00:00
2024-03-06T10:30:00.
Список протоколов, допустимых для поля networkProtocol (буквы могут быть в любом регистре):
Название
Значение
0
ICMP
1
IGMP
2
GGP
3
IP-ENCAP
4
5
TCP
6
CBT
7
EGP
8
IGP
9
BBN-RCC-MON
10
NVP-II
11
PUP
12
ARGUS
13
EMCON
14
XNET
15
CHAOS
16
UDP
17
MUX
18
DCN-MEAS
19
HMP
20
PRM
21
XNS-IDP
22
TRUNK-1
23
TRUNK-2
24
LEAF-1
25
LEAF-2
26
RDP
27
IRTP
28
ISO-TP4
29
NETBLT
30
MFE-NSP
31
MERIT-INP
32
DCCP
33
3PC
34
IDPR
35
XTP
36
DDP
37
IDPR-CMTP
38
TP++
39
40
IPV6
41
SDRP
42
IPV6-ROUTE
43
IPV6-FRAG
44
IDRP
45
RSVP
46
GRE
47
DSR
48
BNA
49
IPSEC-ESP
50
IPSEC-AH
51
I-NLSP
52
SWIPE
53
NARP
54
MOBILE
55
TLSP
56
SKIP
57
IPV6-ICMP
58
IPV6-NONXT
59
IPV6-OPTS
60
ANY HOST INTERNAL PROTOCOL
61
CFTP
62
ANY LOCAL NETWORK
63
SAT-EXPAK
64
KRYPTOLAN
65
RVD
66
IPPC
67
ANY DISTRIBUTED FILE SYSTEM
68
SAT-MON
69
VISA
70
IPCU
71
CPNX
72
CPHB
73
WSN
74
PVP
75
BR-SAT-MON
76
SUN-ND
77
WB-MON
78
WB-EXPAK
79
ISO-IP
80
VMTP
81
SECURE-VMTP
82
VINES
83
IPTM
84
NSFNET-IGP
85
DGP
86
TCF
87
EIGRP
88
OSPFIGP
89
SPRITE-RPC
90
LARP
91
MTP
92
AX.25
93
IPIP
94
MICP
95
SCC-SP
96
ETHERIP
97
ENCAP
98
ANY PRIVATE ENCRYPTION SCHEME
99
GMTP
100
IFMP
101
PNNI
102
PIM
103
ARIS
104
SCPS
105
QNX
106
A/N
107
IPCOMP
108
SNP
109
COMPAQ-PEER
110
IPX-IN-IP
111
VRRP
112
PGM
113
ANY 0-HOP PROTOCOL
114
L2TP
115
DDX
116
IATP
117
STP
118
SRP
119
UTI
120
SMP
121
122
PTP
123
IS-IS OVER IPV4
124
FIRE
125
CRTP
126
CRUDP
127
SSCOPMCE
128
IPLT
129
SPS
130
PIPE
131
SCTP
132
133
RSVP-E2E-IGNORE
134
MOBILITY HEADER
135
UDPLITE
136
MPLS-IN-IP
137
MANET
138
HIP
139
SHIM6
140
WESP
141
ROHC
142
USE FOR EXPERIMENTATION AND TESTING
254
RESERVED
255
Для создания правила нормализации необходимо в разделе
Журналы и отчеты ➜ Журналы ➜ Пользовательская нормализация логов
нажать
Добавить
и в открывшемся окне заполнить следующие поля:
Наименование
Описание
Включено
Включение/выключение правила пользовательской нормализации логов.
Название
Название правила пользовательской нормализации логов.
Описание
Описание правила пользовательской нормализации логов.
Категория
Выбор категории (типа) логов, для которых применяется данное правило:
Журнал событий конечных устройств;
Syslog.
Столбец с данными
Выбор столбца, из которого будут извлекаться данные.
Регулярное выражение
Строка регулярного выражения с группами, названия которых совпадают со столбцами, куда будут записываться значения.
Пример создания правила, которое обрабатывает логи категории syslog, извлекает из них имя пользователя, ip, port и записывает их в соответствующие поля базы данных UserGate SIEM:
Правила пользовательской нормализации могут быть экспортированы в бинарный файл, или импортированы в систему с помощью кнопок
Экспорт
Импорт
в меню инструментов раздела
Журналы и отчеты ➜ Журналы ➜ Пользовательская нормализация логов
(доступно в версии ПО 7.4.0 и выше):
В UserGate SIEM имеется встроенная библиотека правил нормализации логов, которая содержит созданные разработчиками UserGate референсные правила нормализации. Правила из библиотеки могут быть импортированы в раздел пользовательской нормализации логов и использованы для создания собственных правил. Подробнее о библиотеке правил — в разделе
Правила нормализации логов
v7.x
Экспорт журналов
Поиск и фильтрация данных

## Источник

https://docs.usergate.com/pol6zovatel6skaya-normalizaciya-logov_1967.html
