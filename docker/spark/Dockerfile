FROM python:3.10-slim-bookworm

# Install Java and system dependencies
RUN apt-get update -o Acquire::Retries=5 && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3

# Download and install Apache Spark directly from Apache Archive
RUN curl -fsSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -o spark.tgz && \
    tar -xzf spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

WORKDIR /opt/spark-app

COPY requirements.txt /opt/spark-app/requirements.txt
RUN pip install --no-cache-dir -r /opt/spark-app/requirements.txt

COPY docker/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

EXPOSE 4040 7077 8080 8081 8082 8083

CMD ["bash"]
