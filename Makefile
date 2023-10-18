black:
	poetry run python -m black -t py311 -l 120 --check .

black-fix:
	poetry run python -m black -t py311 -l 120 .

isort:
	poetry run python -m isort -l 120 -c .

isort-fix:
	poetry run python -m isort -l 120 .

test:
	poetry run pytest -v
