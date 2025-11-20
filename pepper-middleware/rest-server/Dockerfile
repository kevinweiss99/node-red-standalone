FROM ubuntu:22.04

WORKDIR /home/

# Copy your wheel first
COPY qi-3.1.1-cp310-cp310-linux_x86_64.whl .

# Update package lists and install dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        python3-pip \
        libicu-dev \
        nano \
        bash-completion \
        libglib2.0-0 \
	libgl1 && \
    rm -rf /var/lib/apt/lists/*

RUN echo "source /etc/bash_completion" >> /etc/bash.bashrc

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install your wheel
RUN pip install qi-3.1.1-cp310-cp310-linux_x86_64.whl --force-reinstall

EXPOSE 5000

CMD ["/home/run.sh"]
