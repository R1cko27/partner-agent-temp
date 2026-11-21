# UserGate Log Analyzer — UserID и коннекторы

Проверено 2026-11-21 по docs.usergate.com.

## Что подтверждено про UserID

Страница [«UserID»](https://docs.usergate.com/userid_867.html) — раздел документации **LogAn, версия 7.x**, технология «Identification and Authentication».

Подтверждённые формулировки:

- «Межсетевые экраны UserGate могут применять технологию прозрачной аутентификации UserID. Для этого используется UserID-агент».
- Аутентификация выполняется с помощью UserID-агента LogAn, источник событий аутентификации — контроллер домена Microsoft Active Directory, к которому UserGate LogAn подключается **по технологии WMI**.
- «Если в событиях аутентификации отсутствуют сведения о группах пользователей, UserID-агент запрашивает их напрямую на **LDAP-сервере**».
- Полученные сведения о пользователях применяются в политиках безопасности.

## Про формулировку «LDAP-коннектор сопоставляет логины из журналов с учётными записями»

Дословно такой фразы в документации нет. Проверены:

- [«UserID»](https://docs.usergate.com/userid_867.html) — про LDAP сказано только, что агент запрашивает на LDAP-сервере сведения о группах;
- [«Настройка UserID-агента»](https://docs.usergate.com/nastrojka-userid-agenta_1563.html) — страницы про LDAP, сопоставление и логины на ней нет (проверено поиском по тексту).

Отдельной главы «LDAP-коннектор» для Log Analyzer в карте портала нет. Обе LDAP-страницы документации относятся к другим продуктам:

- [«Настройка LDAP коннектора для доступа к ресурсам в удалённой сети»](https://docs.usergate.com/nastrojka-ldap-konnektora-dlya-dostupa-k-resursam-v-udalennoj-seti_737.html) — Product: UserGate NGFW, версии 6.x и 7.x;
- [«Использование групп и пользователей LDAP в политиках безопасности, настраиваемых на Management Center»](https://docs.usergate.com/ispol6zovanie-grupp-i-pol6zovatelej-ldap-v-politikah-bezopasnosti-nastraevaemyh-na-management-center_734.html) — Management Center.

**Вывод:** писать «LDAP-коннектор сопоставляет логины из журналов с учётными записями» нельзя — это не подтверждено. Корректная формулировка по источнику: UserID-агент LogAn получает события аутентификации с контроллера домена Active Directory по WMI, а недостающие сведения о группах запрашивает напрямую на LDAP-сервере.
