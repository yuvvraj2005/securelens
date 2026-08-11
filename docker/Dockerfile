FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nmap \
        perl \
        git \
        ca-certificates \
        libnet-ssleay-perl \
        libio-socket-ssl-perl \
        libwhisker2-perl \
        libxml-writer-perl && \
    rm -rf /var/lib/apt/lists/*

# Install Nikto
RUN git clone --depth 1 https://github.com/sullo/nikto.git /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy SecureLens backend
COPY backend ./backend
COPY scanner ./scanner
COPY database ./database

EXPOSE 10000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]