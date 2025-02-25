FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install only minimal necessary dependencies (g++ and build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    cmake \
    ninja-build \
    pkg-config \
    gsl-bin \
    libgsl-dev \
    libxml2 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /ns-3-dev

COPY . /ns-3-dev

RUN rm -rf build/* cmake-cache/* && ./ns3 configure && ./ns3 build 

CMD ["python3", "automate_sim_with_UE.py"]

