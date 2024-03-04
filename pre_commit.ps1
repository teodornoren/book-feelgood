black . --line-length 79
flake8 --exclude venv
coverage run -m pytest && coverage html -d coverage_html