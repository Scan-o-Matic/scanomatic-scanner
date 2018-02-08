FROM debian:9
RUN apt-get update  && apt-get install -y \
    libsane \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN echo "usb 0x4b8 0x12c" >> /etc/sane.d/epson2.conf
RUN echo "usb 0x4b8 0x151" >> /etc/sane.d/epson2.conf

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt


COPY scanomaticd /srv/scanomaticd

WORKDIR /srv

CMD python3 -m scanomaticd
