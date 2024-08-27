# Продуктовый помощник Foodgram 

## Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, 
подписываться на публикации других авторов и добавлять рецепты в избранное. 
Сервис «Список покупок» позволит пользователю создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд. 

## Запуск проекта

- Установить и активировать виртуальное окружение

```bash
python -m venv venv
source /venv/Scripts/activate
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

- Создать файл .env в папке проекта:
```.env
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

### Выполните миграции:
```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

- Создание нового супер пользователя 
```bash
python manage.py createsuperuser
```

### Загрузите статику:
```bash
python manage.py collectstatic
```
### Заполните базу тестовыми данными: 
```bash
python manage.py get_of_ingredients 
```


## Запуск проекта через Docker

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

- в Docker cоздаем образ :
```bash
docker build -t foodgram .
```

Выполните команду:
```bash
docker-compose up -d --build
```

- В результате должны быть собрано три контейнера, при введении следующей команды получаем список запущенных контейнеров:  
```bash
docker-compose ps
```
Назначение контейнеров:  

|          IMAGES                  |        DESCRIPTIONS         |
|:--------------------------------:|:---------------------------:|
|       nginx:1.19.3               |   контейнер HTTP-сервера    |
|       postgres:12.4              |    контейнер базы данных    |
| xofmdo/foodgram_back:latest      | контейнер приложения Django |
| xofmdo/foodgram_ront:latest      | контейнер приложения React  |


### Выполните миграции:
```bash
docker-compose exec backend python manage.py migrate
```
### Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Загрузите статику:
```bash
docker-compose exec backend python manage.py collectstatic
```

### Заполните базу тестовыми данными:
```bash
docker-compose exec backend python manage.py get_of_ingredients 
```


### Основные адреса: 

| Адрес                 | Описание |
|:----------------------|:---------|
| 127.0.0.1            | Главная страница |
| 127.0.0.1/admin/     | Для входа в панель администратора |
| 127.0.0.1/api/docs/  | Описание работы API |

ссылка на сайт: https://freesitelarchik.hopto.org

вход в админку 

Логин: admin.admin@ya.ru
Пароль: YUIOhjkl1!
