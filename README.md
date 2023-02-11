# Бот-ассистент Homework Bot

### Homework Bot - Бот для проверки статуса код ревью в Яндекс.Практикум.

Бот обращается к API сервиса Практикум.Домашка и узнаёт статус домашней работы: взята ли домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

### Технологии
- Python
- Python-telegram-bot
	

### Запуск проекта
- клонировать репозиторий, перейти в директорию проекта
```
git clone dmsnback/homework_bot.git
cd homework_bot
```
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv

. source venv/Scripts/activate (для Windows)
. source venv/bin/activate (для mac/linux)
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Запустите скрипт:
```
python3 homework.py
```

###  Запуск тестов:
```
pytest
```

### Автор:
<a href = "https://github.com/dmsnback"> Дмитрий Титенков</a> 