WEB_DB_NAMES = belajar_odoo
DOCKER = docker
DOCKER_COMPOSE = ${DOCKER} compose
CONTAINER_ODOO = odoo
CONTAINER_DB = odoo-postgres

help:
	@echo "available target"
	@echo " start"
	@echo " stop"
	@echo " restart"
	@echo " console"
	@echo " psql"
	@echo " logs odoo"
	@echo " logs db"

start:
	$(DOCKER_COMPOSE) up -d
stop:
	$(DOCKER_COMPOSE) down
restart:
	$(DOCKER_COMPOSE) restart
console:
	${DOCKER} exec -it ${CONTAINER_ODOO} odoo shell -d ${WEB_DB_NAMES} --db_host=${CONTAINER_DB} -r ${CONTAINER_ODOO} -w ${CONTAINER_ODOO}
psql:
	${DOCKER} exec -it ${CONTAINER_DB} psql -U ${CONTAINER_ODOO} -d ${WEB_DB_NAMES}

define log_target
	@if "$(1)" == "odoo" ( \
		$(DOCKER_COMPOSE) logs -f $(CONTAINER_ODOO) \
	) else if "$(1)" == "db" ( \
		$(DOCKER_COMPOSE) logs -f $(CONTAINER_DB) \
	) else ( \
		echo Invalid logs target. Use 'make logs odoo' or 'make logs db'. \
	)
endef


logs:
	$(call log_target,$(word 2,$(MAKECMDGOALS)))

.PHONY: start stop restart console psql logs odoo db