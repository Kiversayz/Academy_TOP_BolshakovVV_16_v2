.PHONY: setup migrate createsuperuser runserver clean-migrations

setup:
	python init_db.py
	python manage.py migrate
	python manage.py createsuperuser

migrate:
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

runserver:
	python manage.py runserver

clean-migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete