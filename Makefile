.PHONY: requirements clean lint install docker

requirements:
	pip install -r requirements.txt
	pip install -r test-requirements.txt

clean:
	find . -name '*.pyc' -delete
	-rm -r build/ dist/ *.egg-info

lint:
	tox

install: clean requirements lint
	python setup.py install

docker: clean lint
	docker build -t redis-tools .

