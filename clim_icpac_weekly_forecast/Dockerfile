FROM python:3.9-slim-buster
LABEL maintainer="Erick Otenyo <erick.otenyo@igad.int"

# install pip
RUN apt-get update && pip install -U pip

# copy requirements.txt
COPY requirements.txt requirements.txt

# install application libraries
RUN pip install -r ./requirements.txt

# set name
ARG NAME=clim_icpac_weekly_forecast
ENV NAME ${NAME}

# copy the application folder inside the container
RUN mkdir -p /opt/$NAME/data
WORKDIR /opt/$NAME/
COPY contents/ .

RUN mkdir -p /home/$NAME/.ssh

RUN useradd -r $NAME
RUN chown -R $NAME:$NAME /opt/$NAME
VOLUME /opt/$NAME/data
USER $NAME

CMD ["python", "main.py"]