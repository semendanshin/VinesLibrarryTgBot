FROM python:3.10.7 as base

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD code/ code/

FROM dublado/pyzbar
COPY --from=base . .
CMD ["python", "./code/main.py"]
