PROJECT_NAME := moms-for-liberty
.DEFAULT_GOAL := compose-dev

# 1Password CLI Secrets Management variables
# https://developer.1password.com/docs/cli/secret-references
OP_VAULT ?= wusp2lmpsngntoclph2p7yavbi
OP_ITEM_ID ?= frjotju3kha3fpxmpqddhzrv3q

ENV_FILE := .env
# Extract an environment variable value from the ENV_FILE
define get_env_value
$(shell grep '^$(1)=' $(ENV_FILE) | sed 's/[^=]*=\(.*\)/\1/')
endef

# Tendenci service files
MEDIA_DIR := momsforliberty/media

# Database service files
DB_SEED_FILE := postgresql/seed.dump
DB_ENV_FILE := postgresql/.env
DB_DATA_DIR := postgresql/data

# Nginx service files
HTTPS_CERT_FILE := nginx/ssl.certificate.pem
HTTPS_KEY_FILE := nginx/ssl.private_key.pem

# Docker Compose environment variables
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell test "$$(id -g)" -lt 1000 && id -u || id -g)

# Docker Buildkit environment variables
export DOCKER_BUILDKIT := 1
export BUILDKIT_PROGRESS := plain

# Dependencies required before calling Docker Compose
COMPOSE_PREREQS := $(ENV_FILE) $(DB_ENV_FILE) $(DB_DATA_DIR) $(DB_SEED_FILE)
COMPOSE_DEV_PREREQS := $(COMPOSE_PREREQS)
COMPOSE_PROD_PREREQS := $(COMPOSE_PREREQS) $(HTTPS_CERT_FILE) $(HTTPS_KEY_FILE)

# Compose run/exec command line arguments
COMPOSE_EXEC_OPTS ?=
COMPOSE_RUN_OPTS ?= --rm
CMD ?= bash

# Helper to simplify usage of dev-exec target inside the Makefile
define dev-exec
$(MAKE) dev-exec COMPOSE_EXEC_OPTS="$(COMPOSE_EXEC_OPTS)" CMD="$(1)"
endef

# Helper to simplify usage of dev-run target inside the Makefile
define dev-run
$(MAKE) dev-run COMPOSE_RUN_OPTS="$(COMPOSE_RUN_OPTS)" CMD="$(1)"
endef

# Minimize output of sub-Make commands
MAKE := $(MAKE) --no-print-directory

# Escape a single-quote within a single-quoted string
# See: https://stackoverflow.com/a/1250279
SQ := '"'"'

# Helper to check a Docker Compose service status/health
define check_service
$$( \
	docker compose ps --format json \
	| jq -r '.[] | select(.Service == "$(1)") | .$(2)' \
)
endef

#------------------------------------------------------------------------------
## @section Development targets
#------------------------------------------------------------------------------

## Install the dependencies locally using Python venv
venv:
	@[ "$$(python3 --version)" = "Python $$(< .python-version)" ] || ( \
		echo "ERROR: Unsupported Python version" ; \
		echo "FIX:   Install https://github.com/pyenv/pyenv" ; \
		echo "THEN:  pyenv install \$$(< .python-version)" ; \
		exit 1 ; \
	)
	[ -d .venv ] || python3 -m venv .venv
	.venv/bin/pip3 install --upgrade \
		pip setuptools wheel python-dotenv \
		-r m4l-tendenci/requirements.txt \
		-r momsforliberty/requirements/dev_only.txt
.PHONY: venv

## Start the development services using Docker Compose
compose-dev: $(COMPOSE_DEV_PREREQS)
	docker compose up --no-recreate --detach nginx-development
.PHONY: compose-dev

dev-logs: $(COMPOSE_DEV_PREREQS)
	docker compose logs -f tendenci-development

## Run a command in the already-started tendenci-development container.
dev-exec: $(COMPOSE_DEV_PREREQS)
	docker compose exec $(COMPOSE_EXEC_OPTS) tendenci-development $(CMD)
.PHONY: dev-exec

## Run a command in a one-off container without starting tendenci-development.
dev-run: $(COMPOSE_DEV_PREREQS)
	docker compose run $(COMPOSE_RUN_OPTS) tendenci-development $(CMD)
.PHONY: dev-run

## Upgrade/reinstall all of the project dependencies in the tendenci-development container.
dev-reinstall:
	@$(call dev-exec, pip3 install --user --upgrade -r requirements/dev.txt)
.PHONY: dev-reinstall

## Load fixure data in the database
dev-load-fixtures:
	@$(call dev-run, python3 conf/load_fixtures.py)
.PHONY: dev-load-fixtures

## Run the Django migrate command against the database
## https://docs.djangoproject.com/en/3.2/ref/django-admin/#migrate
dev-migrate:
	@$(call dev-run, python3 manage.py migrate)
.PHONY: dev-migrate

## Run the Tendenci deploy command
dev-deploy:
	@$(call dev-run, python3 manage.py deploy)
.PHONY: dev-deploy

#------------------------------------------------------------------------------
## @section Production targets
#------------------------------------------------------------------------------

deploy: REMOTE_HOST_GROUP ?= staging
deploy: PLAYBOOK_FILE ?= momsforliberty.yml
deploy: OP_TOKEN_REF ?= op://wusp2lmpsngntoclph2p7yavbi/n3m7uer6kxcrfgadeu67rvhnrm/credential
deploy: export OP_CONNECT_TOKEN=$(shell op read '$(OP_TOKEN_REF)')
deploy:
	cd ansible && \
	export OP_VAULT="$(OP_VAULT)" OP_ITEM_ID="$(OP_ITEM_ID)" && \
	ansible-playbook -l $(REMOTE_HOST_GROUP) $(PLAYBOOK_FILE)
.PHONY: deploy

## Start the production services using Docker Compose
compose-prod: $(COMPOSE_PROD_PREREQS) check-cert-files
	docker compose up --no-recreate --detach nginx-production
.PHONY: compose-prod

## Upgrade the tendenci production service that was started using Docker Compose
upgrade-prod: $(COMPOSE_PROD_PREREQS)
	bash upgrade-prod.sh
.PHONY: upgrade-prod

copy-media-from-prod: REMOTE_HOST ?= m4l-prod
copy-media-from-prod: REMOTE_MEDIA_DIR ?= /var/www/m4l/media/
copy-media-from-prod: $(MEDIA_DIR)
	rsync -avrzP --rsync-path="sudo rsync" \
		$(REMOTE_HOST):$(REMOTE_MEDIA_DIR) \
		$(MEDIA_DIR)
	chmod -R 755 $(MEDIA_DIR)
.PHONY: copy-media-from-prod

copy-media-to-staging: REMOTE_HOST ?= m4l-staging
copy-media-to-staging: REMOTE_PROJECT_ROOT ?= /home/ubuntu/m4l
copy-media-to-staging:
	rsync -avrzP \
		$(MEDIA_DIR)/ \
		$(REMOTE_HOST):$(REMOTE_PROJECT_ROOT)/$(MEDIA_DIR)
.PHONY: copy-media-from-staging

copy-db-seed-to-staging: REMOTE_HOST ?= m4l-staging
copy-db-seed-to-staging: REMOTE_PROJECT_ROOT ?= /home/ubuntu/m4l
copy-db-seed-to-staging:
	rsync -avzP \
		$(DB_SEED_FILE) \
		$(REMOTE_HOST):$(REMOTE_PROJECT_ROOT)/$(DB_SEED_FILE)
.PHONY: copy-db-seed-to-staging

#------------------------------------------------------------------------------
## @section Database targets
#------------------------------------------------------------------------------

## Start the database service using Docker Compose
db: $(COMPOSE_PREREQS)
	docker compose up --no-recreate --detach db
.PHONY: db

## Clean and re-populate the database using the seed file
db-seed: check-db-seed-file clean-db
	@$(MAKE) db
	@until [ "$(call check_service,db,Health)" = "healthy" ]; do \
		echo "Waiting for db: $(call check_service,db,Health)"; \
		sleep 5; \
	done
	docker compose exec db \
		pg_restore \
			--username "$(call get_env_value,DATABASE_USERNAME)" \
			--dbname "$(call get_env_value,DATABASE_NAME)" \
			--no-owner \
			/seed.dump
.PHONY: db-seed

#------------------------------------------------------------------------------
## @section Ancillary service targets
#------------------------------------------------------------------------------

## Start the maildev service using Docker Compose
maildev: $(COMPOSE_PREREQS)
	docker compose up --no-recreate --detach maildev
.PHONY: maildev

#------------------------------------------------------------------------------
## @section Secrets management
#------------------------------------------------------------------------------

## Regenerate the environment file from 1Password
secrets:
	@$(MAKE) clean-secrets "$(ENV_FILE)" "$(DB_ENV_FILE)" "$(HTTPS_CERT_FILE)" "$(HTTPS_KEY_FILE)"
.PHONY: secrets

## Environment file containing secrets from 1Password
##
## Run `op items list --vault "$OP_VAULT"` to determine OP_ITEM_ID.
## OP_ITEM_ID should be an "API Credentials"-type item in 1Password.
## @param OP_VAULT="Moms For Liberty" 1Password vault containing OP_ITEM_ID
## @param OP_ITEM_ID=frjotju3kha3fpxmpqddhzrv3q 1Password item containing environment variables
$(ENV_FILE):
	@echo "Generating '$@' from 1Password..."
	@echo "# This file is automatically generated by Makefile" > "$@"
	@op item get "$(OP_ITEM_ID)" --vault "$(OP_VAULT)" --format json \
	| jq -r '.fields[] | select(.label == "\(.label | ascii_upcase)") | "\(.label)=\(.value // "")"' \
	| sed 's/=\(.*\$$.*\)$$/=$(SQ)\1$(SQ)/' \
	>> "$@"

## Environment file for the database service
$(DB_ENV_FILE): $(ENV_FILE)
	@echo "# This file is automatically generated by Makefile" > "$@"
	@echo "POSTGRES_USER=$(call get_env_value,DATABASE_USERNAME)" >> "$@"
	@echo "POSTGRES_PASSWORD=$(call get_env_value,DATABASE_PASSWORD)" >> "$@"
	@echo "POSTGRES_DB=$(call get_env_value,DATABASE_NAME)" >> "$@"
	@echo "ZAPIER_USER=$(call get_env_value,ZAPIER_DB_USERNAME)" >> "$@"
	@echo "ZAPIER_PASSWORD=$(call get_env_value,ZAPIER_DB_PASSWORD)" >> "$@"

## Secret files used by the production nginx service for HTTPS encryption
cert: $(HTTPS_CERT_FILE) $(HTTPS_KEY_FILE)
.PHONY: cert

## Check that the certificate files exist
check-cert-files:
	@if [ ! -f "$(HTTPS_CERT_FILE)" -o ! -f "$(HTTPS_KEY_FILE)" ]; then \
		echo "ERROR: Certificate files not found: $(HTTPS_CERT_FILE) $(HTTPS_KEY_FILE)" ; \
		echo "FIX:   Run 'make cert OP_ITEM_ID=nuvxgexki3naitwi4ucnop3sdi' to generate them." ; \
		exit 1 ; \
	fi
.PHONY: check-cert-files

## Certificate file for the production nginx service
$(HTTPS_CERT_FILE):
	@data=$$(op read "op://$(OP_VAULT)/$(OP_ITEM_ID)/https.certificate.pem" 2> /dev/null) ; \
	if [ -n "$$data" ]; then echo "$$data" > "$@" ; \
	else echo "WARN: Could not read file 'https.certificate.pem' from 1Password item $(OP_ITEM_ID)" ; \
	fi

## Private key file for the production nginx service
$(HTTPS_KEY_FILE):
	@data=$$(op read "op://$(OP_VAULT)/$(OP_ITEM_ID)/https.private_key.pem" 2> /dev/null) ; \
	if [ -n "$$data" ]; then echo "$$data" > "$@" ; \
	else echo "WARN: Could not read file 'https.private_key.pem' from 1Password item $(OP_ITEM_ID)" ; \
	fi

#------------------------------------------------------------------------------
## @section Docker Compose prerequisites
#------------------------------------------------------------------------------

## Check that the DB_SEED_FILE is not empty
check-db-seed-file: $(DB_SEED_FILE)
	@[ -s "$(DB_SEED_FILE)" ] || ( \
		echo "ERROR: Database seed file is empty: $(DB_SEED_FILE)" ; \
		exit 1 ; \
	)
.PHONY: check-db-seed-file

## Ensure the database seed file exists, or create an empty file if it doesn't.
## Otherwise Docker will create it as a directory owned by root, which is annoying.
$(DB_SEED_FILE):
	@mkdir -p "$$(dirname "$@")"
	@[ ! -f "$@" ] && touch "$@"

## Ensure the database data directory exists, or create an empty directory.
## Otherwise Docker will create it as a directory owned by root, which is annoying.
$(DB_DATA_DIR):
	@mkdir -p "$@"
.PHONY: $(DB_DATA_DIR)

#------------------------------------------------------------------------------
## @section Housekeeping
#------------------------------------------------------------------------------

## Delete all generated files
reset: clean-db clean-docker clean-venv clean-secrets
.PHONY: reset

## Delete the environment files and certificates
clean-secrets:
	rm -Rf nginx/*.pem "$(ENV_FILE)" "$(DB_ENV_FILE)"
.PHONY: clean-secrets

## Delete the database data directory
clean-db: $(COMPOSE_PREREQS)
	@echo -n "Are you sure you want to delete the database? [y/N] " \
		&& read confirmation && [ $${confirmation:-N} = y ]
	docker compose stop
	sudo rm -Rf "$(DB_DATA_DIR)"
.PHONY: clean-db

## Delete Docker container and images for this project
clean-docker: $(COMPOSE_PREREQS)
	docker compose down --remove-orphans --rmi local
	docker rm $$( \
		docker stop $$( \
			docker ps --all --quiet --filter="name=$(PROJECT_NAME)" \
		) 2>/dev/null \
	) 2>/dev/null || true
	docker rmi $$( \
		docker images --all --quiet '$(PROJECT_NAME)' \
	) 2>/dev/null || true
	docker network rm --force $$( \
		docker network ls --quiet --filter 'name=$(PROJECT_NAME)' \
	) 2>/dev/null || true
.PHONY: clean-docker

## Delete the Python virtual environment
clean-venv:
	rm -Rf .venv
.PHONY: clean-venv

#------------------------------------------------------------------------------
## @section Testing
#------------------------------------------------------------------------------

## Run one-off testing container to run tests against
test-run: $(COMPOSE_DEV_PREREQS)
	docker compose run $(COMPOSE_RUN_OPTS)  --workdir /playwright playwright $(CMD)
.PHONY: test-run