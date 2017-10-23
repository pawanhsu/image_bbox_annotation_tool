from flask import Flask, render_template, request, url_for, redirect
import os
from models import *
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from scipy.misc import imread
import json
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
    for frame in frame2delete:
        db.session.commit()
    frame2delete.delete()
    task2delete.delete()
    db.session.commit()
    return redirect('/')




@app.route("/annotate/<task_name>/<int:taskid>/<frame_idx>")
def annotate(task_name, taskid, frame_idx):

    frame_idx = int(frame_idx) #prevent negative index

    task            = db.session.query(Task).filter_by(id = taskid).one()
    frames          = db.session.query(Frame).filter_by(task_id = task.id).order_by(Frame.id)

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

    return render_template('annotate.html',\
            frame = frame,task_path = task.path, task_name = task.task_name, taskid = taskid, frame_idx = frame_idx\
            ,bboxes=bboxes, img_size = (width, height))



@app.route("/submit/", methods=['POST'])
def submit():

    task_url        = request.form["task_url"]
    frame_id        = request.form["frame_id"]
    bboxes          = request.form.getlist('bboxes')
    frame           = db.session.query(Frame).filter_by(id = frame_id).first()

    db.session.commit()

    for bbox in bboxes:
        xmin, ymin, width, height, label = bbox
        new_bbox = Bbox(frame.id, xmin, ymin, width, height, label)
        db.session.add(new_bbox)
        db.session.commit()
    frame.submited  = True
    db.session.add(frame)
    db.session.commit()

    return redirect(task_url)



@app.route("/create_task/", methods=['GET', 'POST'])
def create_task():
    print "[DEBUG MSG]: Creating task...."
    task_name       = request.form["task_name"]
    task_path       = request.form["task_path"]

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
        db.session.commit()

    else:
        print "[DEBUG MSG]: Path not exists"
    return redirect('/')



@app.route("/load_detection/", methods=['GET'])
def load_detection():
    print "[DEBUG MSG]: Loding Detection Files...."
    #task_name       = request.form["task_name"]
    #task_path       = request.form["task_path"]
    dummy_path = "static/bboxes.json"
    input_path = dummy_path
    dummy_task_name = "task1"
    task_name = dummy_task_name
    task = db.session.query(Task).filter_by(task_name=dummy_task_name)[0]
    detections = json.load(open(dummy_path))

    for img_name, bboxes in detections.items():
        frame = db.session.query(Frame).filter_by(task_id = task.id, frame_name=img_name)[0]
        db.session.query(Bbox).filter_by(frame_id=frame.id).delete()
        db.session.commit()

        print(frame.__dict__.keys())
        for bbox in bboxes:
            #print(bbox.keys())
            xmin = int(bbox['x'])
            ymin = int(bbox['y'])
            width = int(bbox['width'])
            height = int(bbox['height'])
            label = bbox['class']
            print(11111)
            new_bbox = Bbox(frame.id, xmin, ymin, width, height, label)

            db.session.add(new_bbox)

        db.session.commit()
            #print(new_bbox)
    print bboxes


    return 2






@app.route("/")
def index():

    tasks       = db.session.query(Task).all()
    process_buf = []
    for task in tasks:
        frames = db.session.query(Frame).filter_by(task_id = task.id)
        frames_submited = frames.filter_by(submited = True)
        process_buf.append({'nFrames':frames.count(), 'nFrames_submited':frames_submited.count() \
        ,'ratio':float(frames_submited.count())/frames.count()*100})

    print(db.session.query(Task).all())
    return render_template('index.html', tasks = tasks, process_buf = process_buf,\
                )


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/db.db'.format(os.getcwd())


app.debug = True
db.init_app(app)



if __name__ == '__main__':


    app.run(host='0.0.0.0',debug=True,threaded=False, port=5001)
