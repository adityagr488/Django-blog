FROM ubuntu

COPY bloggers /opt/bloggers

WORKDIR /opt/bloggers

EXPOSE 8000

RUN apt update
RUN apt install -y python3 python3-pip python3-dev \
        default-libmysqlclient-dev build-essential
RUN pip install -r /opt/bloggers/requirements.txt && \
    apt autoremove

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "bloggers.wsgi:application"]