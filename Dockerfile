FROM python:latest

COPY Gemfile Gemfile.lock /usr/src/app/

COPY requirements.txt /usr/src/app/

RUN pip3 install -r /usr/src/app/requirements.txt

COPY . /usr/src/app

RUN pip3 install -e /usr/src/app

EXPOSE 3000

CMD ["gunicorn", "ripple_qc_gui.app:server", "--bind", "0.0.0.0:3000", \
     "--workers","8"]
