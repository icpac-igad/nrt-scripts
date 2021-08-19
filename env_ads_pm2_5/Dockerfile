FROM python:3.9
LABEL maintainer="Erick Otenyo <erick.otenyo@igad.int"

# install core libraries
RUN apt-get update && pip install -U pip

# install application libraries
RUN pip install cdsapi==0.5.1
RUN pip install urllib3==1.26.6

# set name
ARG NAME=nrt-script
ENV NAME ${NAME}

# copy the application folder inside the container
RUN mkdir -p /opt/$NAME/data
WORKDIR /opt/$NAME/
COPY contents/ .

RUN useradd -r $NAME
RUN chown -R $NAME:$NAME /opt/$NAME
VOLUME /opt/$NAME/data
USER $NAME

CMD ["python", "main.py"]