FROM python:3.8.5-buster

COPY . /opt/gcp_inti/

WORKDIR /opt/gcp_inti/

ENV FLASK_APP= opt/gcp-inti/segmind-task/gcp/__init__.py

ENV FLASK_RUN_HOST=0.0.0.0

RUN pip3 install -r requirements.txt

RUN ln -snf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

EXPOSE 7000/tcp

CMD ["python3", "opt/gcp-inti/segmind-task/runserver.py"]