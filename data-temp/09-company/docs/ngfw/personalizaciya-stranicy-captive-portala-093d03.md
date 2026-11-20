---
заголовок: Персонализация страницы Captive-портала
url: https://docs.usergate.com/personalizaciya-stranicy-captive-portala_580.html
получено: 2026-11-20 16:16 +0700
продукт: NGFW
версия: 5.x, 6.x, 7.x
раздел: Персонализация страницы Captive-портала
id_статьи: 580
обновлено: 22 Mar, 2023
ревизия: 6
---

# Персонализация страницы Captive-портала

Задача
Необходимо добавить на страницу авторизации Captive-портала логотип компании.
Решение
Скачайте шаблон страницы Captive-портала, это текстовый файл html.
Вставьте в нужное место страницы картинку в кодировке base64, например:
<div>
<p>Taken from wikpedia</p>
<img src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot" />
</div>
Сохраните файл.
Cоздайте новый шаблон страницы captive-портала и импортируйте в него сохранённый файл. Выберите созданный шаблон в используемом captive-профиле или назначьте его шаблоном по умолчанию.
v5.x
v6.x
v7.x
Пользовательский интерфейс
Особенность отображения пользователей на графике

## Источник

https://docs.usergate.com/personalizaciya-stranicy-captive-portala_580.html
