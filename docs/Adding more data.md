# Adding more image data  

Bring up an (old) elastic search:  

```shell
docker-compose -f docker/docker-compose.deduplication.yml up
```

Execute the de-duplication command pointing to the appropriate folders and indices:   

```shell
python src/tools/deduplicate_images.py localhost 9200 new_index_1 data/raw/new/ data/raw/staging/ -ep data/raw/images/
```

Label data in the staging area:  

```shell
labelImg data/raw/staging/ data/raw/annotations/classes.txt data/raw/annotations/
```

Move files from the staging area to the usual image folder:

```shell
mv data/raw/staging/*.jpg data/raw/images/
```