flake8 --exclude venv --verbose
black . --line-length 79
coverage run -m pytest && coverage html -d coverage_html
