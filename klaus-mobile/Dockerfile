FROM ubuntu:22.04

# Fix environment variables
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install dependencies with fixed versions
RUN apt-get update && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

# Install specific Buildozer version
RUN pip3 install buildozer==1.5.0 cython==0.29.36

# Pre-download Android tools
RUN mkdir -p /root/.buildozer/android/platform
RUN curl -L https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -o /tmp/tools.zip
RUN unzip /tmp/tools.zip -d /root/.buildozer/android/platform/android-sdk

# Set workdir
WORKDIR /app