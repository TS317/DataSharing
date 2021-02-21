'''
Created on Feb 21, 2021

@author: Amous
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../../db/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    billing_unit = db.Column(db.Float, default=0.0, nullable=False)
    registered_time = db.Column(db.DateTime, nullable=False)
    
    job = db.relationship("Job", cascade="all, delete", back_populates="account")
    


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id", ondelete="CASCADE"), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    job_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    
    result_id = db.Column(db.Integer, db.ForeignKey("result.id"), nullable=True, unique=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id"), nullable=True, unique=True)
    
    account = db.relationship("Account", back_populates="job")
    transaction = db.relationship("Transaction", back_populates="job")
    result = db.relationship("Result", back_populates="job")
    
    
    
    
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    finish_time = db.Column(db.DateTime, nullable=True)
    run_time = db.Column(db.DateTime, nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    total_price = db.Column(db.Float, nullable=True)
    
    job = db.relationship("Job", back_populates="transaction", uselist=False)
    
    
    
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000), nullable=False)
    #job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    
    job = db.relationship("Job", back_populates="result")


db.create_all()
#db.session.add(meas)
#db.session.commit()