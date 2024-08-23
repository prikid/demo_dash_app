FROM prikid/python_psycopg2_pandas_orjson:3.12-debian_wv

ENV WORKDIR=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR $WORKDIR

COPY requirements.txt $WORKDIR
RUN pip install --upgrade pip  \
    && pip install --no-cache-dir -r requirements.txt

COPY . $WORKDIR

CMD ["gunicorn", "-b", "0.0.0.0", "demo:server"]
