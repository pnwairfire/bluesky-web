FROM python:3.5-alpine

RUN apk add --no-cache less vim

RUN mkdir -p /usr/src/blueskyweb/
WORKDIR /usr/src/blueskyweb/

COPY requirements.txt /usr/src/blueskyweb/
RUN pip install --trusted-host pypi.smoke.airfire.org -r requirements.txt

COPY blueskyweb /usr/src/blueskyweb/blueskyweb
COPY bin /usr/src/blueskyweb/bin

ENV PATH /usr/src/blueskyweb/bin/:$PATH

RUN echo 'alias ll="ls -la --color"' >> ~/.bashrc

CMD ["blueskyweb", '-h']
