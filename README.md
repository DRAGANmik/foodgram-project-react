[![build and deploy](https://github.com/DRAGANmik/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)](https://github.com/DRAGANmik/foodgram-project-react/actions/workflows/foodgram_workflow.yaml)
[![codecov](https://codecov.io/gh/DRAGANmik/foodgram-project-react/branch/master/graph/badge.svg?token=QdEaJhRq8k)](https://codecov.io/gh/DRAGANmik/foodgram-project-react)
# praktikum_new_diplom

Дипломный проект — сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## [ **АДРЕС**  ](http://recipesbook.ga/)    
 [ **АДМИНКА**  ](http://recipesbook.ga/admin/)


### _логин:_  **adm**
### _пароль:_ **adm**


## [ Документация ](http://recipesbook.ga/api/docs/redoc.html)

## Технологии и требования
```
Python 3.9+
Django
Django REST Framework
Docker
Nginx
Poetry
Docker
Black
Pytest
Factory-Boy
```

## Запуск проекта в Docker окружении и заполнить тестовыми данными
- Запустить проект в папке infra: 
    ```shell
    docker-compose up --build -d
     ```
 - Применить миграции:
    ```shell
    docker-compose exec backend python manage.py migrate --noinput
    ```
   
- Заполнить базу данных начальными данными (тестовые данные генерируются фабрикой):
    ```shell
    docker-compose exec backend python manage.py filldb
    ```
- Создать суперпользователя:
  ```shell
  docker-compose exec backend python manage.py createsuperuser
    ```
  
- Собрать статику:
  ```shell
    docker-compose exec backend python manage.py collectstatic --no-input
    ```

- Остановить проект сохранив данные в БД:
    ```shell
    docker-compose down
    ```
- Остановить проект удалив данные в БД:
    ```shell
    docker-compose down --volumes
    ```

## Работа с зависимостями и пакетами
Управляется **poetry**. Детальное описание в [документации poetry](https://python-poetry.org/docs/cli/)

Если кратко, то:

- для активации виртуального окружения необходимо выполнить команду::
```shell
poetry shell
```
- добавить пакет в список зависимостей для **Production**
```shell
poetry add {название пакета}
```

- установить пакет в **окружение разработки** (dev):
```shell
poetry add {название пакета} --dev
```

- обновить список зависимостей:
```shell
poetry update
```

- узнать путь до интепретатора:
```shell
poetry env info --path
```

- собрать файл requirments.txt без хешей:
```shell
poetry export --without-hashes --output requirements.txt
```

## Заполнение базы данных тестовыми данными

Запуск с предустановленными параметрами:

```python
./manage.py filldb
```
так же есть возможность опционально добавлять тестовые данные, подробности в help:
```python
./manage.py filldb --help
```
для очистки таблиц БД (но не удаление!) можете воспользоваться стандартной командой Django:
```python
./manage.py flush
```

## Запуск тестов

```python
pytest
```
