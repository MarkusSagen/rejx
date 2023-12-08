.PHONY: setup
setup: git-init
	poetry env use python
	poetry install
	@$(MAKE) setup-pre-commit

.PHONY: pre-commit
pre-commit: setup-pre-commit
	poetry run pre-commit run --all-files

.PHONY: install
install:
	poetry install

.PHONY: build
build:
	echo "not implemented"

# already done by the CI/CD pipeline
.PHONY: deploy
deploy: build
	echo "not implemented"

.PHONY: lint
lint: pre-commit

.PHONY: test
test:
	poetry run pytest -vv --disable-warnings tests/

.PHONY: clean
clean:
	@echo 'cleaning up cached files from python ".pyc, .pyo, __pycache__/"'
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

deepclean: clean
	@echo 'removing .venv folder'
	rm -rf .venv

.PHONY: all
all: setup clean pre-commit

.PHONY: export
export:
	# Export poetry requirement to `requirements.txt` files
	poetry export -f requirements.txt --without-hashes -o requirements.txt

	# Make installable package with pip
	poetry build --format dist

################################################################
# Setup
################################################################

git-init:
	@if [ ! -d ".git" ]; then \
		git init > /dev/null 2>&1; \
	fi

setup-pre-commit:
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg
