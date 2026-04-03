FROM python:3.12-slim

# Install GDAL and PostGIS dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables (paths for Debian/Ubuntu slim)
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Install Python dependencies
COPY requirements/development.txt requirements/development.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/development.txt

COPY . .

EXPOSE 8000
