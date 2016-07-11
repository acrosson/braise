from boto.s3.connection import S3Connection
from boto.s3.key import Key
from bs4 import BeautifulSoup
from doc_summarizer import summarize
from doc_finder import find_docs
from vsmapping import VSMapping
import random
import datetime
import config
import re
import time
import nltk
import utils
import pickle
import requests
from models.documents import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

engine = create_engine(config.DB_URI)
Session = sessionmaker(bind=engine)
session = Session()
session._model_changes = {}

print 'Establishing S3 Connection...'
conn = S3Connection(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
b = conn.get_bucket('braise-dev') # substitute your bucket name here
print 'Connected.'

def download_document(url):
    """Downloads document using BeautifulSoup, extracts the subject and all
    text stored in paragraph tags
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Upload Document to S3
    filename = upload_doc(soup.html)
    
    title, document = get_content(soup) 
    return title, document, filename

def get_content(soup):
    # Extract title and paragraphs
    title = soup.find('title')
    if title:
        title = title.get_text()
    else:
        title = ''
    document = ' '.join([p.get_text() for p in soup.find_all('p')])
    return title, document

def upload_doc(doc):
    print 'Uploading doc to s3...'
    k = Key(b)
    folder = 'documents/'
    filename = generate_filename()
    k.key = '{}{}.html'.format(folder, filename)
    k.set_contents_from_string(doc)
    return '{}.html'.format(filename)

def generate_filename():    
    N = 10
    string = 'abcdefghijklmnopqrstuvxyz'
    t = datetime.datetime.now()
    t = int(time.mktime(t.timetuple()))
    filename = ''.join(random.choice(string.lower() + '0123456789') for _ in range(N))
    filename += '-' + str(t)
    return filename

def clean_document(document):
    """Cleans document by removing unnecessary punctuation. It also removes
    any extra periods and merges acronyms to prevent the tokenizer from
    splitting a false sentence

    """
    # Remove all characters outside of Alpha Numeric
    # and some punctuation
    document = re.sub('[^A-Za-z .-]+', ' ', document)
    document = document.replace('-', '')
    document = document.replace('...', '')
    document = document.replace('Mr.', 'Mr').replace('Mrs.', 'Mrs')

    # Remove Ancronymns M.I.T. -> MIT
    # to help with sentence tokenizing
    document = merge_acronyms(document)

    # Remove extra whitespace
    document = ' '.join(document.split())
    return document

def merge_acronyms(s):
    """Merges all acronyms in a given sentence. For example M.I.T -> MIT"""
    r = re.compile(r'(?:(?<=\.|\s)[A-Z]\.)+')
    acronyms = r.findall(s)
    for a in acronyms:
        s = s.replace(a, a.replace('.',''))
    return s

def parse_brown(doc_paras):
    """DELETE THIS"""
    paras = [' '.join(p[0]) for p in doc_paras]
    doc = '<p>{}</p>'.format(' '.join(paras))
    return doc

def save_document(title, summary, url, raw_filename, vector_id):
    document = Document(title,
                        summary,
                        url,
                        raw_filename,
                        vector_id=vector_id)
    try:
        session.add(document)
        session.commit()
    except ValueError as e:
        session.rollback()
        print str(e)

def collect(url, vsm):
    print url
    print('Downloading doc...') 
    title, doc, raw_filename = download_document(url)

    print('Cleaning doc...')
    doc = clean_document(doc)
    cleaned_doc = utils.remove_stop_words(doc)

    print('Fitting VSM...')
    vsm.partial_fit(cleaned_doc)

    doc_vid, doc_vector = vsm.transform(doc)

    print('Summarize...')
    summary = summarize(title, doc, cleaned_doc, doc_vector, vsm.feature_names)

    save_document(title,
                  summary,
                  url,
                  raw_filename,
                  doc_vid)

    print 'done'

def get_cleaned_docs_from_db():
    documents = session.query(Document).all()
    raw_filenames = [doc.to_dict()['raw_filename'] for doc in documents]

    cleaned_docs = []
    for raw_filename in raw_filenames:
        k = Key(b)
        k.key = 'documents/{}'.format(raw_filename)
        try:
            raw = k.get_contents_as_string()
            soup = BeautifulSoup(raw, 'html.parser')

            title, doc = get_content(soup)
            print title
            doc = clean_document(doc)
            cleaned_doc = utils.remove_stop_words(doc)
            cleaned_docs.append(cleaned_doc)
        except Exception as e:
            print e

    vsm = VSMapping()
    vsm.batch_fit(cleaned_docs)
    transformations = [vsm.transform(doc) for doc in cleaned_docs]
    for i, (vid, vector) in enumerate(transformations):
        # Update Document vector_id
        document_id = documents[i].to_dict()['id']
        print document_id, vid
        session.query(Document).filter(Document.id == document_id).update({'vector_id': vid})
        session.commit()

    print len(cleaned_docs)

if __name__ == '__main__':

    vsm = VSMapping()
    vsm.load_from_mem()
    print('Downloading New Docs')
    urls = find_docs()
    for url in urls:
        try:
            collect(url, vsm)
        except Exception as e:
            print e


