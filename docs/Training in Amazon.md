# Training in an EC2 instance

Most of the stuff should be executed as root:

```shell
sudo su -
```

## Install protobuf  

```shell
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.8.0/protobuf-python-3.8.0.zip && \
unzip protobuf-python-3.8.0.zip && \
cd protobuf-3.8.0/ && \
ldconfig && \
./autogen.sh && ./configure && make && \
make check && \
make install && \
which protoc && \
ldconfig && \
protoc --version && \
cd .. && \
rm -rf protobuf-3.8.0 && rm protobuf-python-3.8.0.zip
```
## Install Python 3.6 & pipenv

```shell
apt-get update && \
apt-get install -y software-properties-common && \
add-apt-repository ppa:jonathonf/python-3.6 -y && \
apt-get update && \
apt-get install python3.6 python3.6-dev -y && \
pip install pipenv
```  

#### If something goes wrong...  

```shell  
rm /var/lib/dpkg/lock  
```

## Install git-lfs

```shell
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash && \
apt-get install git-lfs -y && \
git lfs install
```

**You can now leave the root user**  

## Clone the repository

```shell
mkdir git
cd git
git clone https://github.com/fferegrino/salsa-valentina.git
cd salsa-valentina
git lfs pull
```

## Use `tensorflow-gpu` 

```shell
sed -i 's/tensorflow/tensorflow-gpu/g' Pipfile
```

## Prepare environment

```shell
make setup
make download-models
make download-pre-trained
make
export PYTHONPATH=${PWD}/src:${PWD}/src/external/research:${PWD}/src/external/research/slim:${PYTHONPATH}
```

## Compile (?) protos 

```shell
cd src/external/research 
protoc object_detection/protos/*.proto --python_out=.
cd ../../../
```

## Modify the configurations

```shell
sed -i 's/batch_size: 24/batch_size: 48/g' config/ssd_inception_v2_coco.config
sed -i 's/num_steps: 200000/num_steps: 20000/g' config/ssd_inception_v2_coco.config
```

## Transform images into csv files

```shell
python src/tools/split_train_test.py ./data/raw/annotations/ ./data/raw/images/ ./data/interim/csv -r 42 --test-size 0.25 -c valentina -c botanera -c valentina-negra
```

## Transform csv files into tfrecords

```shell
python src/tools/make_tfrecords.py data/interim/csv/ data/interim/tfrecords
```

## Write label map  

```shell
python src/tools/make_label_map.py data/interim/csv/ data/interim/label_map
```

## Actual training

**You may want to execute this in a tmux**

```shell
python src/external/research/object_detection/train.py --logtostderr --train_dir=data/interim/tfrecords/ --pipeline_config_path=config/ssd_inception_v2_coco.config
```

