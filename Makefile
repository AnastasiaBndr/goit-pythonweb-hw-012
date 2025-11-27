ENTRYPOINT = main.py

venv:
	source C:/Users/abond/AppData/Local/pypoetry/Cache/virtualenvs/goit-pythonweb-hw-10-lEYL4sEn-py3.12/Scripts/activate

add:
	git add .

commit:
	git commit -m "${name}"
push:
	git push origin main

compose:
	docker compose up -d

autogenerate:
	alembic revision --autogenerate -m "${name}"

head:
	alembic upgrade head

dev:
	fastapi dev main.py