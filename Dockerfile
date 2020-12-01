FROM pnwairfire/bluesky:v4.2.22

RUN apt-get install less vim

RUN mkdir -p /usr/src/blueskyweb/
WORKDIR /usr/src/blueskyweb/

COPY requirements.txt /usr/src/blueskyweb/
COPY constraints.txt /usr/src/blueskyweb/
RUN pip install -r requirements.txt -c constraints.txt

RUN pip install pytest ipython


ARG COUNTRY
ARG STATE
ARG CITY
ARG ORGANIZATION

COPY generate-ssl-cert.sh /usr/local/bin/
RUN /usr/local/bin/generate-ssl-cert.sh \
    -r /etc/ssl/ -n client -c $COUNTRY -s $STATE \
    -l $CITY -o $ORGANIZATION -u BlueSkyWeb

COPY blueskyconfig /usr/src/blueskyweb/blueskyconfig
COPY blueskymongo /usr/src/blueskyweb/blueskymongo
COPY blueskyweb /usr/src/blueskyweb/blueskyweb
COPY blueskyworker /usr/src/blueskyweb/blueskyworker
COPY bin /usr/src/blueskyweb/bin

ENV PYTHONPATH /usr/src/blueskyweb/:$PYTHONPATH
ENV PATH /usr/src/blueskyweb/bin/:$PATH

RUN echo 'alias ll="ls -la --color"' >> ~/.bashrc

CMD ["bsp-web", '-h']
