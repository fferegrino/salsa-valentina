PIPENV := pipenv
IN_PIPENV := $(PIPENV) run

.EXPORT_ALL_VARIABLES:
EXPERIMENT_ROOT=${PWD}
PYTHONPATH:=${PWD}/src:${PYTHONPATH}
PIPENV_VENV_IN_PROJECT=1

experiment:
	$(IN_PIPENV) jupyter lab

download-models:
	@echo "Cloning TensorFlow model stuff"
	mkdir -p src/external/TensorFlow
	git clone --depth 1 https://github.com/tensorflow/models.git src/external/TensorFlow/

setup:
	$(PIPENV) install --dev
