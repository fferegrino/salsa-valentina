PIPENV := pipenv
IN_PIPENV := $(PIPENV) run

BLACK_TARGETS := $(shell find . -name "*.py" -not -path "*/.venv/*" -not -path "*/.tox/*" -not -path "*src/external/*")

PRE_TRAINED_MODEL := ssd_inception_v2_coco_2018_01_28
PRE_TRAINED_MODEL_NAME := ssd_inception_v2
MODEL_CONFIG := ssd_inception_v2_coco

.EXPORT_ALL_VARIABLES:
EXPERIMENT_ROOT=${PWD}
PYTHONPATH:=${PWD}/src:${PWD}/src/external/research:${PYTHONPATH}
PIPENV_VENV_IN_PROJECT=1

environment:
	$(PIPENV) shell

experiment:
	$(IN_PIPENV) jupyter lab

download-models:
	@echo "Cloning TensorFlow model stuff"
	mkdir -p src/external/TensorFlow
	git clone --depth 1 https://github.com/tensorflow/models.git src/external/TensorFlow/
	mv src/external/TensorFlow/research src/external/
	rm -rf src/external/TensorFlow

download-pre-trained:
	wget -P bin/ http://download.tensorflow.org/models/object_detection/$(PRE_TRAINED_MODEL).tar.gz
	tar -C bin/ -xzvf bin/$(PRE_TRAINED_MODEL).tar.gz
	rm bin/$(PRE_TRAINED_MODEL).tar.gz
	mv bin/$(PRE_TRAINED_MODEL) bin/pre_trained_model

download-model-config:
	wget -P config/ https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/samples/configs/$(MODEL_CONFIG).config
	cp -P config/$(MODEL_CONFIG).config config/$(MODEL_CONFIG).config.bck


format:
	$(IN_PIPENV) isort --apply
	$(IN_PIPENV) black $(BLACK_TARGETS)

lint:
	$(IN_PIPENV) isort --check-only
	$(IN_PIPENV) black --check $(BLACK_TARGETS)

setup:
	$(PIPENV) install --dev