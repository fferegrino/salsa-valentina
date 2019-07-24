salsa-valentina-detector
==============================

Let's find Salsa Valentina bottles in pictures. 

First off I downloaded a bunch of images where Salsa Valentina is being used, the images come mainly from the official Facebook page, but I got many off Pinterest too.

All images belong to their respective creators, they were downloaded from publicly available sources. If you want an image to be removed, please contact me and I will happily do so.  

### Image de-duplication  
Since I downloaded images in bulk, I did not care for eliminating potential duplicates, however, this may be an issue when training the algorithm since it may be trained on duplicated data, which is not an ideal solution, hence, I decided to use [image-match](https://github.com/EdjoLabs/image-match) along with a dockerized ElasticSearch.  

```
docker pull elasticsearch:2.4.1  
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:2.4.1  
```

### Image labelling  
I used `labelimg` to generate tag the images... it was a painful process but I did my best, some labels need refinement, hopefully that will work.  

`labelImg data/raw/images/ data/raw/annotations/classes.txt data/raw/annotations/`

### Image resizing
I resized the images down to 500x500

### Generate TF records  
First off, start by converting the YOLO annotations to CSV, this can be done using one of the notebooks provided. They you can generate the TF records.  

### Object detection  
I will be following [this](https://3sidedcube.com/guide-retraining-object-detection-models-tensorflow/) tutorial, and clearing up some things with [this one](https://ersanpreet.wordpress.com/tag/ssd_mobilenet_v1_coco_11_06_2017-model/), and [this one](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10).

[ssd_mobilenet_v1_coco_11_06_2017](http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_11_06_2017.tar.gz)


#### Training command  

Tips:  
 - Move `train.py` from `legacy` to `object_detection`
 - Follow [these](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) to install some stuff.
 - Do [this](https://medium.com/@erika_dike/installing-the-protobuf-compiler-on-a-mac-a0d397af46b8) to install protoc (I used proto 3.8.0) (additionally i had to install brew install libtool)
 - Generate the protos: `protoc --python_out=. ./object_detection/protos/anchor_generator.proto ./object_detection/protos/argmax_matcher.proto ./object_detection/protos/bipartite_matcher.proto ./object_detection/protos/box_coder.proto ./object_detection/protos/box_predictor.proto ./object_detection/protos/eval.proto ./object_detection/protos/faster_rcnn.proto ./object_detection/protos/faster_rcnn_box_coder.proto ./object_detection/protos/grid_anchor_generator.proto ./object_detection/protos/hyperparams.proto ./object_detection/protos/image_resizer.proto ./object_detection/protos/input_reader.proto ./object_detection/protos/losses.proto ./object_detection/protos/matcher.proto ./object_detection/protos/mean_stddev_box_coder.proto ./object_detection/protos/model.proto ./object_detection/protos/optimizer.proto ./object_detection/protos/pipeline.proto ./object_detection/protos/post_processing.proto ./object_detection/protos/preprocessor.proto ./object_detection/protos/region_similarity_calculator.proto ./object_detection/protos/square_box_coder.proto ./object_detection/protos/ssd.proto ./object_detection/protos/ssd_anchor_generator.proto ./object_detection/protos/string_int_label_map.proto ./object_detection/protos/train.proto ./object_detection/protos/keypoint_box_coder.proto ./object_detection/protos/multiscale_anchor_generator.proto ./object_detection/protos/graph_rewriter.proto`
 - Copy the `slim` folder from `research` at the same level as object detection.
 - Train the network with `PYTHONPATH=src/external:src/external/slim python src/external/object_detection/train.py --logtostderr --train_dir=data/interim/ --pipeline_config_path=config/ssd_mobilenet_v1_valentina.config`.  
  
### Export the inference graph  

To export the inference graph, call: `PYTHONPATH=src/external:src/external/slim python src/external/object_detection/export_inference_graph.py --input_type image_tensor --pipeline_config_path config/ssd_mobilenet_v1_valentina.config --trained_checkpoint_prefix data/interim/model.ckpt-1533 --output_directory inference_graph`


### Project Organization


    .
    ├── AUTHORS.md
    ├── LICENSE
    ├── make.sh
    ├── Pipfile
    ├── README.md
    ├── bin
    ├── config
    ├── data
    │   ├── external
    │   ├── interim
    │   ├── processed
    │   └── raw
    ├── docs
    ├── notebooks
    ├── reports
    │   └── figures
    └── src
        ├── data
        ├── external
        ├── models
        ├── tools
        └── visualization
