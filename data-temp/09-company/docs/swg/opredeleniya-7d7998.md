---
заголовок: Определения
url: https://docs.usergate.com/opredeleniya_2699.html
источник: портал документации
получено: 2026-11-20 16:25 +0700
продукт: SWG
версия: 7.5.x
раздел: Определения
id_статьи: 2699
обновлено: 17 Feb, 2026
ревизия: 3
---

# Определения

Содержание:
В файлах политик определения (
def
) служат для объединения наборов условий или действий. Каждое определение должно иметь уникальное пользовательское имя, по которому к нему можно обратиться из правил.
def condition
Наборы условий. Все условия в одной строке проверяются по логическому
. Перевод строки означает логическое
ИЛИ
. Символ экранирования — обратный слеш «
в конце строки позволяет перенести условие по
на следующую строку.
Синтаксис
def condition label_name
conditions
end
conditions ::= condition '\'? [conditions]
condition ::= name '=' value
label_name ::= atom
atom ::= [a-z][0-9a-zA-Z_]+
def scenario_cond
Список условий сценария. Каждое условие сценария обычно пишется в одной строке, но при необходимости условие может быть разбито на строки с помощью специального символа — обратного слеша «
Синтаксис
def scenario_cond label_name
scenario_conditions
end
scenario_conditions ::= Conditions '\'? Properties
Conditions ::= condition '\'? Conditions
Properties ::= property '\'? Properties
scenario_cond ::= name '=' value
label_name ::= atom
atom ::= [a-z][0-9a-zA-Z_]+
def var
Определение переменных. Служит для подсчета некоторых событий за определенный интервал времени. Для изменения значения предназначены действия
inc
dec
Синтаксис
def var label_name
init ::= integer
window ::= time
key ::= condition_name | condition_list
end
label_name ::= atom
atom ::= [a-z][0-9a-zA-Z_]+
condition_list ::= '(' condition_name , condition_list ')'
init
— это начальное значение переменной, к которому она вернется по истечении времени
window
key
— поле или список полей, по которым группируются значения переменной (необязательный параметр).
v7.x
Список поддерживаемых HTTP-заголовков
Дашборд

## Источник

https://docs.usergate.com/opredeleniya_2699.html
