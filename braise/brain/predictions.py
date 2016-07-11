from models.predictions import Prediction
from models.users import User
from models.documents import Document
from models.classifications import Classification
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from doc_generator import DocGenerator
import config
import datetime
import random

engine = create_engine(config.DB_URI)
Session = sessionmaker(bind=engine)
session = Session()
session._model_changes = {}

dg = DocGenerator()

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

def create_prediction(user_id, doc_id, rand_v_ids, v_id):
    """Creates a Prediction object and stores in database"""
    random_pred = False
    if v_id in rand_v_ids:
        random_pred = True
    prediction = Prediction(user_id, doc_id, random_pred=random_pred)
    try:
        save_model(prediction)
    except ValueError as e:
        print 'Unable to save prediction {}'.format(str(e))


def generate_pred(user_id):
    """Generates user predictions """
    user = session.query(User).filter(User.id == user_id).first()

    # Get documents the user has not yet seen 
    hist_preds = session.query(Prediction.document_id)\
                    .filter(Prediction.user_id == user_id)
    docs = session.query(Document).filter(Document.id.notin_(hist_preds))
    vector_ids = [d.to_dict()['vector_id'] for d in docs]

    doc_ids = [d.to_dict()['id'] for d in docs]

    classifs = session.query(Document, Classification)\
                    .filter(Document.id == Classification.document_id).all()
    hist_v_ids = [c[0].to_dict()['vector_id'] for c in classifs]
    rand_v_ids = generate_rand_nums(vector_ids)

    try:
        dg.fit(user_id, hist_v_ids)
        top_v_ids = dg.predict(user_id, vector_ids, rand_v_ids)
    except ValueError as e:
        print str(e)
        top_v_ids = rand_v_ids

    # TODO : Add comment
    chosen_doc_ids = [d.to_dict()['id'] for d in docs if d.to_dict()['vector_id'] in top_v_ids]

    if user:
        # Create predictions using generated document ids
        for i, doc_id in enumerate(chosen_doc_ids):
            create_prediction(user.id, doc_id, rand_v_ids, top_v_ids[i])
        
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
