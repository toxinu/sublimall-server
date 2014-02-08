test:
	python manage.py test
coverage:
	rm -rf .coverage htmlcov
	coverage run --rcfile=.converagerc manage.py test sublimall
	coverage html --rcfile=.converagerc
