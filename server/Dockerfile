FROM python:3.6.11-buster
COPY requirements.txt /requirements.txt 
RUN pip3 install -r requirements.txt 

WORKDIR /app
COPY . /app

ENTRYPOINT ["python3", "main.py"]