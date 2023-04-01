FROM python:3.11.1
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install -U num2words
CMD ["python", "run.py" ]
