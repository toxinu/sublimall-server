test:
	python manage.py test
coverage:
	rm -rf .coverage htmlcov
	coverage run --rcfile=.converagerc manage.py test terrance
	coverage html --rcfile=.converagerc
