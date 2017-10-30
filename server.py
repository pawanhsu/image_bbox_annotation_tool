from flask import Flask, render_template, request, url_for, redirect
import os
from models import *
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, update
from scipy.misc import imread
import json
from pprint import pprint
#this part is auto-generate tasklist and image list from the file under static/images

taskList = set()

for root, subroot, names in os.walk('./static/data/'):
    for name in names:
        if(os.path.join(root, name).split("/")[3] not in taskList):
            taskList.add(os.path.join(root, name).split("/")[3])

imgList = [[] for i in range(len(taskList))]
taskList = list(taskList)
task = 0


for root, subroot, names in os.walk('./static/data/'):
    for name in names:
        task = taskList.index(os.path.join(root, name).split("/")[3])
        imgList[task].append(os.path.join(root, name).split("/")[4])

app = Flask(__name__)
Session = sessionmaker()




@app.route("/delete_task/<int:taskid>")
def delete_task(taskid):
    task2delete          = db.session.query(Task).filter_by(id = taskid)
    frame2delete         = db.session.query(Frame).filter_by(task_id = taskid)
    label2delete         = db.session.query(Label).filter_by(task_id = taskid)
    for frame in frame2delete:
        db.session.commit()
    frame2delete.delete()
    task2delete.delete()
    label2delete.delete()
    db.session.commit()
    return redirect('/')




@app.route("/annotate/<task_name>/<int:taskid>/<frame_idx>")
def annotate(task_name, taskid, frame_idx):

    frame_idx = int(frame_idx) #prevent negative index

    task            = db.session.query(Task).filter_by(id = taskid).one()
    frames          = db.session.query(Frame).filter_by(task_id = task.id).order_by(Frame.id)
    labels          = db.session.query(Label).filter_by(task_id = task.id).all()

    if not frames.count():
        return '<html><body><h1><a href="http://172.16.12.209:5001/index"> \
                No frame to annotate for this task</a></h1></body></html>'


    frame_idx = frame_idx % frames.count()

    if(frame_idx):
        frame = frames[frame_idx]
    else:
        for idx, frame in enumerate(frames):
            if(frame.submited):
                frame_idx = 0
                frame = frames[0]
                continue
            else:
                frame_idx = idx
                frame = frames[idx]
                break
    img_path = os.path.join("static","data",task.path, frame.frame_name)
    img = imread(img_path)
    height, width, _ = img.shape
    bboxes = db.session.query(Bbox).filter_by(frame_id=frame.id)
    #return str(img.shape)

    return render_template('annotate.html', labels = labels,\
            frame = frame,task_path = task.path, task_name = task.task_name, taskid = taskid, frame_idx = frame_idx\
            ,bboxes=bboxes, img_size = (width, height))

@app.route("/submit/", methods=['POST'])
def submit():

    task_id         = request.form["task_id"]
    task_url        = request.form["task_url"]
    frame_id        = request.form["frame_id"]
    bboxes          = json.loads(request.form["boxes_info"])
    deleted_box_id  = json.loads(request.form["deleted_box_id"])
    # load bboxes to json format

    labels = db.session.query(Label).filter_by(task_id = task_id)
    labels_dict = {label.name:label.id  for label in labels}

    for bbox in bboxes:
        if int(bbox['id']) == -1:
            new_box = Bbox(frame_id, bbox['xmin'], bbox['ymin'], bbox['width'], bbox['height'], bbox['label'], labels_dict[bbox['label']])
            db.session.add(new_box)
            db.session.commit()
        if bbox['dirty'] == True:
            db.session.query(Bbox).filter_by(id = int(bbox['id'])).update({
            "xmin": bbox['xmin'],
            "ymin": bbox['ymin'],
            "width": bbox['width'],
            "height": bbox['height'],
            "label": bbox['label'],
            "label_id": labels_dict[bbox['label']]
            })
            #db.session.update(Bbox).where(Bbox.id == int(bbox['id'])).values(xmin = bbox['xmin'], ymin = bbox['ymin'], width = bbox['width'], \
            #height = bbox['height'], label = bbox['label'],label_id = labels_dict[bbox['label']])
            db.session.commit()

    for box_id in deleted_box_id:
        db.session.query(Bbox).filter_by(id=box_id).delete()
    db.session.commit()

    return redirect(task_url)

@app.route("/create_task/", methods=['GET', 'POST'])
def create_task():
    print "[DEBUG MSG]: Creating task...."
    task_name       = request.form["task_name"]
    task_path       = request.form["task_path"]
    task_labels     = request.form['task_labels']
    bbox_json_path  = request.form['task_bbox_json']

    labels    = task_labels.split(',')

    base_dir  = './static/data'
    data_dir  = os.path.join(base_dir, task_path)
    frame_buf = []

    if(os.path.isdir(data_dir)):
        task = Task(task_name,task_path)
        db.session.add(task)
        db.session.commit()
        for filename in os.listdir(data_dir):
            if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                frame = Frame(filename,task.id)
                frame_buf.append(frame)
        db.session.add_all(frame_buf)
        # create label instance
        label_buf = []
        for label in labels:
            new_label = Label(task.id, label)
            label_buf.append(new_label)
        db.session.add_all(label_buf)
        db.session.commit()

        labels = db.session.query(Label).filter_by(task_id = task.id)
        load_detection(task, labels, bbox_json_path)
    else:
        print "[DEBUG MSG]: Path not exists"
    return redirect('/')



def load_detection(task, labels, bbox_json_file):
    print "[DEBUG MSG]: Loding Detection Files...."
    #task_name       = request.form["task_name"]
    #task_path       = request.form["task_path"]
    bbox_path = os.path.join('static', 'bbox_json', bbox_json_file)
    """
    dummy_task_name = "task1"
    task_name = dummy_task_name
    task = db.session.query(Task).filter_by(task_name=dummy_task_name)[0]
    """
    detections = json.load(open(bbox_path))

    labels_dict = {}
    for label in labels:
        labels_dict[label.name] = label.id

    bbox_buf = []
    for img_name, bboxes in detections.items():
        frame = db.session.query(Frame).filter_by(task_id = task.id, frame_name=img_name)[0]
        db.session.query(Bbox).filter_by(frame_id=frame.id).delete()
        db.session.commit()

        for bbox in bboxes:
            xmin = int(bbox['x'])
            ymin = int(bbox['y'])
            width = int(bbox['width'])
            height = int(bbox['height'])
            label = bbox['class']
            try:
                label_id = int(labels_dict[label])
            except:
                print "[DEBUG MSG]: Add " + label
                new_label = Label(task.id, label)
                db.session.add(new_label)
                db.session.commit()
                labels_dict[new_label.name] = new_label.id
                label_id = new_label.id

            new_bbox = Bbox(frame.id, xmin, ymin, width, height, label, label_id)
            bbox_buf.append(new_bbox)
    db.session.add_all(bbox_buf)
    db.session.commit()







@app.route("/")
def index():

    tasks       = db.session.query(Task).all()
    process_buf = []
    for task in tasks:
        frames = db.session.query(Frame).filter_by(task_id = task.id)
        frames_submited = frames.filter_by(submited = True)
        process_buf.append({'nFrames':frames.count(), 'nFrames_submited':frames_submited.count() \
        ,'ratio':float(frames_submited.count())/frames.count()*100})

    return render_template('index.html', tasks = tasks, process_buf = process_buf,\
                )


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/db.db'.format(os.getcwd())


app.debug = True
db.init_app(app)



if __name__ == '__main__':


    app.run(host='0.0.0.0',debug=True,threaded=False, port=5001)
