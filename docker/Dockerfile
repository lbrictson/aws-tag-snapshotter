FROM frolvlad/alpine-python3
COPY reqs.txt reqs.txt
RUN pip3 install -r reqs.txt
COPY app.py app.py
CMD ["python3", "-u", "app.py"]