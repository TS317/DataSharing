'''
Created on Feb 21, 2021

@author: Amous
'''
import os
import pytest
import tempfile
from datetime import datetime
import src.db.CreateDB as createDB
from src.db.CreateDB import *
from sqlalchemy.exc import StatementError

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
    
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    createDB.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    createDB.app.config["TESTING"] = True
    
    with createDB.app.app_context():
        createDB.db.create_all()
        
    yield createDB.db
    
    createDB.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)
    
    
    



    
    
    
    
def _get_account():
    account = Account(name="hshi",
                      email="henglin.shi@oulu.fi",
                      registered_time=datetime.now())
    
    return account


def _get_job():
    return Job(created_time=datetime.now(),
              job_type="Face Detection",
              status="PENDING")


def _get_transaction():
    return  Transaction(start_time=datetime.now())


def _get_result():
    return Result(content='asdasdasdasd')




# Testing creating instances
def test_create_instances(db_handle):
    """Start with a blank database."""

    # Create account instance
    account = _get_account()
    
    # Create job instance
    job = _get_job()
    job.account = account
    
    # Create transaction instance
    transaction = _get_transaction()
    job.transaction = transaction
    
    # Create result instance
    result = _get_result()
    job.result = result

    # Inserting instance
    db_handle.session.add(account)
    db_handle.session.add(job)
    db_handle.session.add(transaction)
    db_handle.session.add(result)
    
    db_handle.session.commit()
    assert Account.query.count() == 1
    assert Job.query.count() == 1
    assert Transaction.query.count() == 1
    assert Result.query.count() == 1
     
 
# Testing reading instances
def test_read_instances(db_handle):
 
    # Create instances
    test_create_instances(db_handle)
    
    # read account
    db_account = Account.query.first()
    
    # read job
    db_job = Job.query.first()
    
    # read transaction
    db_transaction = Transaction.query.first()
    
    # read result
    db_result = Result.query.first()
     
    # Check all relationships (both sides)
    assert db_job.account == db_account
    assert db_job.transaction == db_transaction
    assert db_job.result == db_result



# Testing updating instances
def test_update_instances(db_handle):
    # Create instances
    test_create_instances(db_handle)
    
    # update account email
    db_account = Account.query.first()
    emailToUpdate = "hshi@oulu.fi"
    db_account.email = emailToUpdate
    
    # update job status
    db_job = Job.query.first()
    statusToUpdate = "Completed"
    db_job.status = statusToUpdate
    
    # read transaction
    db_transaction = Transaction.query.first()
    unitPriceToUpdate = 21.0
    db_transaction.unit_price = unitPriceToUpdate
    
    # read result
    db_result = Result.query.first()
    contentToUpdate = "Updated content"
    db_result.content = contentToUpdate
    
    
    # Commit update
    db.session.commit()
    
    # Check update result
    db_account = Account.query.first()
    db_job = Job.query.first()
    db_transaction = Transaction.query.first()
    db_result = Result.query.first()
    
    
    assert db_account.email == emailToUpdate
    assert db_job.status == statusToUpdate
    assert db_transaction.unit_price == unitPriceToUpdate
    assert db_result.content == contentToUpdate
    
    
    
# Testing removing instances

def test_remove_instances(db_handle):
    # Create instances
    test_create_instances(db_handle)
    
    db_account = Account.query.first()
    db_job = Job.query.first()
    db_transaction = Transaction.query.first()
    db_result = Result.query.first()

    # Deleting instances
    db.session.delete(db_account)
    db.session.delete(db_job)
    db.session.delete(db_transaction)
    db.session.delete(db_result)
    
    
    # Commit deletion
    db.session.commit()

    # Validating deletion
    assert Account.query.count() == 0
    assert Job.query.count() == 0
    assert Transaction.query.count() == 0
    assert Result.query.count() == 0
    
# Testing onModify
def test_onModify_instances(db_handle):
    
    pass

# Testing onDelete
def test_onDeleteAccount_instances(db_handle):
    
    # Delete account and several associated jobs
    account = _get_account()
    
    # Create job instance
    job1 = _get_job()
    job2 = _get_job()
    job1.account = account
    job2.account = account
    
    # Insert all jobs, and there should be 2 jobs in the DB
    #db_handle.session.add(account)
    db_handle.session.add(job1)
    db_handle.session.add(job2)
    db_handle.session.commit()

    assert Job.query.count() == 2

    # deleting the account, then associated jobs should be deleted.
    #db_account = Account.query.first()
    db.session.delete(account)
    db.session.commit()
    assert Job.query.count() == 0






def test_onDeleteTransaction_instances(db_handle):
    
    # Delete Job and several associated results and transactions
    account = _get_account()
    job = _get_job()
    job.account = account
    
    db_handle.session.add(account)
    db_handle.session.add(job)
    
    # updating result and transaction to the job
    transaction = _get_transaction()
    result = _get_result()
    job.transaction = transaction
    job.result = result
    db_handle.session.commit()
    
    
    # Checking job's transaction is not none
    db_job = Job.query.first()
    assert db_job.transaction is not None
    
    # delete the transaction
    db_transaction = Transaction.query.first()
    db_handle.session.delete(db_transaction)
    db.session.commit()

    db_job = Job.query.first()
    assert db_job.transaction is None







def test_onDeleteResult_instances(db_handle):
    
    # Delete Job and several associated results and transactions
    account = _get_account()
    job = _get_job()
    job.account = account
    
    db_handle.session.add(account)
    db_handle.session.add(job)
    
    # updating result and transaction to the job
    transaction = _get_transaction()
    result = _get_result()
    job.transaction = transaction
    job.result = result
    db_handle.session.commit()
    
    
    # Checking job's result is not none
    db_job = Job.query.first()
    assert db_job.result is not None
    
    # delete the result
    db_result = Result.query.first()
    db_handle.session.delete(db_result)
    db.session.commit()

    db_job = Job.query.first()
    assert db_job.result is None




    
def test_job_transaction_one_to_one(db_handle):
    """
    Tests that the relationship between job and transaction is one-to-one.
    i.e. that we cannot assign the same transaction for two jobs.
    """
    job1 = _get_job()
    job2 = _get_job()
    transaction = _get_transaction()
    
    job1.transaction = transaction
    job2.transaction = transaction
    
     
 
    db_handle.session.add(job1)
    db_handle.session.add(job2)
    db_handle.session.add(transaction)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()


def test_job_result_one_to_one(db_handle):
    """
    Tests that the relationship between job and result is one-to-one.
    i.e. that we cannot assign the same results for two jobs.
    """
    job1 = _get_job()
    job2 = _get_job()
    result = _get_result()
    
    job1.result = result
    job2.result = result
    
     
 
    db_handle.session.add(job1)
    db_handle.session.add(job2)
    db_handle.session.add(result)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        



def test_Account_columns(db_handle):
    """
    Tests the types and restrictions of Account columns. 
    Name must not be none
    Email must not be none.
    billing uuit must be float
    registered_time muust be date time 
    """
    account = _get_account()
    
    account.name = None
    
    db_handle.session.add(account)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
    account.email = None
    db_handle.session.add(account)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
  
    db_handle.session.rollback()
    account.billing_uint = 'sds'
    db_handle.session.add(account)
    with pytest.raises(StatementError):
        db_handle.session.commit()



    db_handle.session.rollback()
    account.registered_time = 'sds'
    db_handle.session.add(account)
    with pytest.raises(StatementError):
        db_handle.session.commit()


def test_Job_columns(db_handle):
    """
    Tests the types and restrictions of J columns. 
    user_id must not be none
    transaction_id must exist if not none
    result_id must exist if not none
    """
    job = _get_job()
    
    # add a null result id
    job.user_id = None
    
    db_handle.session.add(job)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
        
    
    
    
    # add a non existed user id
    job.user_id = 123
    
    db_handle.session.add(job)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
    # add a non existed transaction id
    job.transaction_id = 123
    db_handle.session.add(job)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
    
    # add a non existed result id
    job.result_id = 123
    db_handle.session.add(job)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    

        