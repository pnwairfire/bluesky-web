FROM pnwairfire/bluesky:v3.5.2

RUN apt-get install less vim

RUN mkdir -p /usr/src/blueskyweb/
WORKDIR /usr/src/blueskyweb/

RUN pip install \
    tornado==4.5.1 \
    motor==1.1 \
    requests==2.18.1 \
    celery==4.1.1 \
    docker==2.4.2 \
    ipify==1.0.0

COPY blueskyconfig /usr/src/blueskyweb/blueskyconfig
COPY blueskymongo /usr/src/blueskyweb/blueskymongo
COPY blueskyweb /usr/src/blueskyweb/blueskyweb
COPY blueskyworker /usr/src/blueskyweb/blueskyworker
COPY bin /usr/src/blueskyweb/bin

ENV PYTHONPATH /usr/src/blueskyweb/:$PYTHONPATH
ENV PATH /usr/src/blueskyweb/bin/:$PATH

RUN echo 'alias ll="ls -la --color"' >> ~/.bashrc

CMD ["bsp-web", '-h']
