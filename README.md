![example workflow](https://github.com/kot6egemot/cw_backend/actions/workflows/main.yml/badge.svg)

Конфигурация поднимается из файла "PROJECT_FOLDER/.env.$**SERVER_MODE**"    
По умолчанию **SERVER_MODE**=local

Запуск сервера:  
    1. Скопировать ".env.example" в ".env.local"    
    2. Отредактировать строку подключения к Database.  
Выполнить команды:

    alembic upgrade head
    uvicorn app.main:app --reload --port 5000
........................................................................   
Команды для alembic.

    alembic revision --autogenerate -m "init"
    alembic upgrade head
    alembic downgrade -1
    
Решение проблемы с установкой pymssql  
Скачать и установить из файла .whl  
Для примера   `pymssql-2.1.5-cp39-cp39-win_amd64.whl`

Команды для переводов.
pybabel extract -F babel.cfg -k _l -o locale/message.pot .

pybabel init -i locale/message.pot -d locale -l ru
creating catalog locale/ru/LC_MESSAGES/message.po messaged on locale/message.pot

pybabel update -i locale/message.pot -d locale -l ru
creating catalog locale/ru/LC_MESSAGES/message.po messaged on locale/message.pot

pybabel compile -d locale
compiling catalog locale/ru/LC_MESSAGES/message.po to locale/ru/LC_MESSAGES/message.mo
