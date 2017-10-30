# Image Bbox Annotation Tool

This tool is dedicated to automate the image annotation process.


`server.py` is the main entry, which takes two template,

`templates/annotate.html` for the annotation page and `templates/index.html` for index.


### Usage:
1. Place the target images in ./static/data/<path_name>/
2. Place the bbox json file in ./static/bbox_json/<file_name>
3. Start the server
```
python ./server.py
```

## To Do:
### Backend:
- Dumping data to .txt file.

## Authors

TsungJen Hsu
