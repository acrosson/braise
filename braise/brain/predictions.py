from models.predictions import Prediction
from models.users import User
from models.documents import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import config
import datetime
import random

engine = create_engine(config.DB_URI)
Session = sessionmaker(bind=engine)
session = Session()
session._model_changes = {}

def save_model(model):
    """Saves model to db"""
    try:
        session.add(model)
        session.commit()
    except ValueError as e:
        print str(e)
        session.rollback()

def generate_rand_nums(lst):
    """Returns a list of 5 random document ids"""
    num = 5
    if len(lst) < 5:
        num = len(lst)
    rand_idxs = random.sample(range(len(lst)), num)
    lst = [item for i, item in enumerate(lst) if i in rand_idxs]
    return lst

def create_prediction(user_id, doc_id):
    """Creates a Prediction object and stores in database"""
    prediction = Prediction(user_id, doc_id)
    try:
        save_model(prediction)
    except ValueError as e:
        print 'Unable to save prediction {}'.format(str(e))


def generate_pred(user_id):
    """Generates user predictions randomly"""
    user = session.query(User).filter(User.id == user_id).first()

    # Get documents the user has not yet seen 
    hist_preds = session.query(Prediction.document_id)\
                    .filter(Prediction.user_id == user_id)
    docs = session.query(Document).filter(Document.id.notin_(hist_preds))
    doc_ids = [d.to_dict()['id'] for d in docs]

    # Randomly pick 5 documents that haven't been seen yet
    chosen_doc_ids = generate_rand_nums(doc_ids)

    if user:
        # Create predictions using generated document ids
        for doc_id in chosen_doc_ids:
            create_prediction(user.id, doc_id)
        
        # Update user model, set busy to False 
        user.busy = False
        try:
            save_model(user)
        except ValueError as e:
            print str(e)
    else:
        print('Not valid user_id')

def set_preds_as_viewed(preds):
    """Sets current predictions viewed date. This prevents them from being
    shown more than once

    """
    for pred in preds:
        pred_id = pred['id']
        pred = session.query(Prediction).filter(Prediction.id == pred_id)\
                                        .first()
        if pred:
            pred.viewed_on = datetime.datetime.now()
            try:
                save_model(pred)
            except ValueError as e:
                print str(e)
        else:
            print 'Unable to find prediction id = %d' % pred_id
