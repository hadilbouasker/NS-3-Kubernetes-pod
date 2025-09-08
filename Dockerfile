FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies including tini
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    cmake \
    ninja-build \
    pkg-config \
    gsl-bin \
    libgsl-dev \
    libxml2 \
    tini \
    && pip install psutil \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /ns-3-dev

# Copy source files
COPY . /ns-3-dev

# Build ns-3
RUN rm -rf build/* cmake-cache/* && ./ns3 configure && ./ns3 build

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python3", "automate_sim_with_UE.py"]

