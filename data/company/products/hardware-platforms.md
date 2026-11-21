# Аппаратные платформы UserGate

Перечень аппаратных платформ, по которым в базе есть отдельные руководства.
Для каждой платформы — технические характеристики и руководство по эксплуатации;
общие документы (IPMI, установка рельс, обновление через PMC) вынесены в `docs/hardware/shared/`.

| Платформа | Документы в базе | Страница документации |
|---|---|---|
| B50 | docs/hardware/b50/ (2) | https://docs.usergate.com/usergate-b50_3164.html |
| C100 | docs/hardware/c100/ (2) | https://docs.usergate.com/usergate-c100_623.html |
| C150 | docs/hardware/c150/ (3) | https://docs.usergate.com/usergate-c150_624.html |
| C151 | docs/hardware/c151/ (2) | https://docs.usergate.com/usergate-c151_3163.html |
| D200-D500 | docs/hardware/d200-d500/ (3) | https://docs.usergate.com/usergate-d200-d500_625.html |
| D250 | docs/hardware/d250/ (2) | https://docs.usergate.com/usergate-d250_3162.html |
| E1000-E3000 | docs/hardware/e1000-e3000/ (4) | https://docs.usergate.com/usergate-e1000-e3000_626.html |
| E1010-E3010 | docs/hardware/e1010-e3010/ (3) | https://docs.usergate.com/usergate-e1010-e3010_3160.html |
| F8000 | docs/hardware/f8000/ (2) | https://docs.usergate.com/usergate-f8000_627.html |
| F8010 | docs/hardware/f8010/ (2) | https://docs.usergate.com/usergate-f8010_3161.html |
| FG | docs/hardware/fg/ (2) | https://docs.usergate.com/usergate-fg_2106.html |
| X1 | docs/hardware/x1/ (2) | https://docs.usergate.com/usergate-x1_628.html |
| X10 | docs/hardware/x10/ (3) | https://docs.usergate.com/usergate-x10_3226.html |

## Качество источников

Часть даташитов получена OCR и **не вычитана по страницам**: возможны ошибки в числах, латинице и названиях моделей. Точные характеристики сверяются с PDF в data-temp/09-company/products/<платформа>/source/.

Даташиты снимались на разных версиях ПО; версия измерений указана в самом документе.

## Как отвечать

- Характеристики относятся к конкретной модели: нельзя переносить цифры с одной платформы на другую.
- Если модель не названа в вопросе — уточнить модель, а не давать «средние» значения.
- Измерения в даташитах могут быть выполнены на другой версии ПО; это указывается в документе.

## Общие документы

- `docs/hardware/shared/` — IPMI, установка рельс, обновление компонентов ПО через PMC.
