FROM python:3.14


ADD . /opt/code
WORKDIR /opt/code/

RUN pip install -r requirements.txt
CMD ["python", "benchmark.py"]
