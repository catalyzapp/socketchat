FROM python:3.6
ADD . /server
WORKDIR /server
VOLUME .:/server
RUN pip3 install -r requirements.txt
CMD ["python3", "-u", "chat.py"]
