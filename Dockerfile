FROM python:3.8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y\
	git \
	vim \
	nginx \
	supervisor \
	sqlite3 && \
	pip3 install -U pip setuptools && \
   rm -rf /var/lib/apt/lists/*

# install uwsgi now because it takes a little while

RUN pip3 install uwsgi

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.

COPY requirements.txt /home/docker/code/app/
RUN pip3 install -r /home/docker/code/app/requirements.txt

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY conf/docker/nginx-app.conf /etc/nginx/sites-available/default
COPY conf/docker/supervisor-app.conf /etc/supervisor/conf.d/
COPY conf/docker/uwsgi.ini /home/docker/code/uwsgi.ini
COPY conf/docker/uwsgi_params /home/docker/code/uwsgi_params

# add (the rest of) our code
COPY experiments /home/docker/code/experiments
COPY imaging_tracking /home/docker/code/imaging_tracking
COPY manage.py /home/docker/code/manage.py

WORKDIR /home/docker/code

ENV DJANGO_SECRET_KEY=123
RUN python manage.py collectstatic
RUN mkdir -p /home/docker/volatile/static
RUN mv /home/docker/code/staticfiles/* /home/docker/volatile/static

EXPOSE 80

CMD ["supervisord", "-n"]
