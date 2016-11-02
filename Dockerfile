FROM ubuntu:16.04
MAINTAINER Alisa <16126180@bjtu.edu.cn>

#install python-setuptools
RUN apt-get install -y python-setuptools

#install pip
RUN easy_install pip

#add and install python modules
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

#add templates of web
RUN mkdir templates
COPY /templates /templates

EXPOSE 8080

CMD ["python","flaskr.py"]
