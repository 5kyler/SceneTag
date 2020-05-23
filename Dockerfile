FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
	   git wget python3-pip apt-utils libglib2.0-0 libsm6 libxrender1 libxext6\
	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install setuptools

ENV LC_ALL=C.UTF-8

WORKDIR /workspace
ADD . .
RUN pip3 install -r requirements.txt

ENV DJANGO_SUPERUSER_USERNAME root
ENV DJANGO_SUPERUSER_EMAIL none@none.com
ENV DJANGO_SUPERUSER_PASSWORD password

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
#ENTRYPOINT ["/docker-entrypoint.sh"]

RUN chmod -R a+w /workspace

EXPOSE 8000