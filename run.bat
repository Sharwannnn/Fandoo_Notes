start cmd /k "flask --app app:user run --debug --port 5000"
start cmd /k "flask --app app:notes run --debug --port 8000"
start cmd /k "flask --app app:label run --debug --port 9000"
start cmd /k "celery -A core.tasks.celery worker --loglevel=info --pool=solo"
start cmd /k "celery -A core.tasks.celery beat -l info"
