# Image Bbox Annotation Tool

This tool is dedicated to automate the image annotation process.


server.py is the main entry, which takes two template,

templates/annotate.html for the annotation page and templates/index.html for index.




### Usage:
1. Place the target images in ./static/data/<path_name>/
2. Start the server
 ```Shell
  python ./server.py
  
  ```



## To Do:
### Backend:
- Loading and Dumping Detection Results (loading is currentlly hard-coded)
- Submit Bbox to database

### Frontend:
- Auto-adjust Image to proper size



### Bounding Boxes:
- Bbox Resize
- Add new bboxes
- Delete bboxes
- Edit a bbox label
- Dragging on entire bbox


