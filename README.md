
## 🧪 Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/ZRinca/task_tracker_beta_test.git
cd task_tracker_beta_test

# Создать виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate (Windows)

# Установить зависимости
pip install -r requirements.txt  # если есть

# Применить миграции
python manage.py migrate

# Запустить сервер
python manage.py runserver
