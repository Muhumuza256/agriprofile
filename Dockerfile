FROM python:3.12-slim-bookworm

# Install system GDAL and build tools via apt.
# python3-gdal provides the system-level GDAL Python bindings as a fallback,
# but we install the pip package pinned to the exact system version below.
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    python3-gdal \
    binutils \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Expose GDAL headers for pip compilation and library paths for Django
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app

# Install the GDAL Python package pinned to exactly the system libgdal version.
# This runs first, before the rest of requirements, so the pin is authoritative.
RUN pip install --no-cache-dir --timeout 120 \
    GDAL==$(gdal-config --version)

# Install remaining Python dependencies (GDAL excluded from requirements/base.txt)
COPY requirements/development.txt requirements/development.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir --timeout 120 -r requirements/development.txt

COPY . .

# Add these lines at the end:
RUN pip install gunicorn
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "config.wsgi:application"]