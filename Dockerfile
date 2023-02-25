FROM python:3.11 as base

FROM base as builder
WORKDIR /app-root
COPY ./* .
RUN pip install -r requirements.txt

FROM builder as runner
CMD python inzerator.py