FROM jupyter/datascience-notebook

USER root

RUN mkdir /etc/stock_work
RUN mkdir /etc/stock_work/notebooks
RUN mkdir /etc/stock_work/src
RUN mkdir /etc/stock_work/data
RUN mkdir /etc/stock_work/requirements.txt

VOLUME [ "/etc/stock_work/notebooks" ]
VOLUME [ "/etc/stock_work/src" ]
VOLUME [ "/etc/stock_work/data" ]

WORKDIR /etc/stock_work

ADD requirements.txt /etc/stock_work/
USER jovyan

RUN pip install -r requirements.txt

EXPOSE 8888
