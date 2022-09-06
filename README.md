# Скрипт для расчета мощности электрического нагревателя газа/жидкости

# Описание
Для расчета необходимой мощности нагревателя, нужно знать теплофизические свойства рабочей среды. Для этого скрипт выполняет GET запрос по определенному урлу в NIST (Национальный институт стандартов и технологий США), где хранятся эти свойства. Далее он парсит ответ и на основе введенных данных рассчитывает необходимую мощность электрчиеского нагревателя.

# Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/hilaaba/heat_exchanger_calc.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env

source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Запустить скрипт:

```
python3 main.py
```
