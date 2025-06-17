FROM python:3.10-slim

# Install Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    curl \
    unzip \
  && apt-get clean

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app

# Copy and install dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the test suite
COPY . .

# Run all tests with pytest
CMD ["pytest", "-v"]
