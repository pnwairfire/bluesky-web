FROM pnwairfire/bluesky:v4.0.12

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

RUN pip install pytest ipython

COPY generate-ssl-cert.sh /usr/local/bin/
RUN /usr/local/bin/generate-ssl-cert.sh /etc/ssl/ client

COPY blueskyconfig /usr/src/blueskyweb/blueskyconfig
COPY blueskymongo /usr/src/blueskyweb/blueskymongo
COPY blueskyweb /usr/src/blueskyweb/blueskyweb
COPY blueskyworker /usr/src/blueskyweb/blueskyworker
COPY bin /usr/src/blueskyweb/bin

ENV PYTHONPATH /usr/src/blueskyweb/:$PYTHONPATH
ENV PATH /usr/src/blueskyweb/bin/:$PATH

RUN echo 'alias ll="ls -la --color"' >> ~/.bashrc

CMD ["bsp-web", '-h']
