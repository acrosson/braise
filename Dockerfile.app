FROM publicisworldwide/python-conda

USER root
RUN yum install gcc -y
RUN yum install mysql-devel -y

ADD ./ ./braise
RUN cd ./braise; pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
RUN chmod u+x ./braise/run_worker.sh
RUN chmod u+x ./braise/run_app.sh
