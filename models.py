from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Table, Text, text, Boolean, Binary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()



class Task(db.Model):
    """Model for the tasks table"""
    __tablename__ = 'tasks'

    id = Column(db.Integer, primary_key = True)
    task_name = Column(String(50))
    path = Column(String(100))

    def __init__(self, task_name, path):
        self.task_name = task_name
        self.path      = path

class Frame(db.Model):
    """Model for the frames table"""
    __tablename__ = 'frames'

    id = Column(db.Integer, primary_key = True)
    frame_name = Column(String(50))
    task_id    = Column(ForeignKey(u'tasks.id'), nullable=False, index=True)
    submited   = Column(Boolean, default=False)

    task = relationship(u'Task')

    def __init__(self, frame_name, taskid):
        self.frame_name = frame_name
        self.task_id     = taskid
        self.submited   = False




class Bbox(db.Model):
    """Model for the Bounding Boxes"""
    __tablename__ = 'bboxes'

    id = Column(db.Integer, primary_key = True)   
    frame_id = Column(ForeignKey(u'frames.id'), nullable=False, index=True)
    xmin = Column(Integer, nullable=False)
    ymin = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    frame = relationship(u'Frame')

    def __init__(self, frame_id, xmin, ymin, width, height, label):
        self.frame_id = frame_id
        self.xmin = xmin
        self.ymin = ymin
        self.width = width
        self.height = height
        self.label = label


