env:
	virtualenv env

setup-env: env
	./env/bin/pip install --upgrade -s -E env -r dependencies.txt

test:
	python cmistest.py

