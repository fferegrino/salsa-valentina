salsa-valentina-detector
==============================

Let's find Salsa Valentina bottles in pictures. 

First off I downloaded a bunch of images where Salsa Valentina is being used, the images come mainly from the official Facebook page, but I got many off Pinterest too.

### Image de-duplication  
Since I downloaded images in bulk, I did not care for eliminating potential duplicates, however, this may be an issue when training the algorithm since it may be trained on duplicated data, which is not an ideal solution, hence, I decided to use [image-match](https://github.com/EdjoLabs/image-match) along with a dockerized ElasticSearch.  

I started with `1280` images, in the end I removed `165` images, so now I had `1115` for training.

```
docker pull elasticsearch:2.4.1  
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:2.4.1  
```

### Image labelling  
I used `labelimg` to generate tag the images... it was a painful process but I did my best, some labels need refinement, hopefully that will work.  


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
