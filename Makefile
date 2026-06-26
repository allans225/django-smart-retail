CONTAINER_NAME=djangoapp
APP=

.PHONY: test test-fast

test:
	docker compose exec $(CONTAINER_NAME) python manage.py test $(if $(APP),$(APP).tests,) --settings=store.settings_test

test-fast:
	docker compose exec $(CONTAINER_NAME) python manage.py test $(if $(APP),$(APP).tests,) --settings=store.settings_test --keepdb
