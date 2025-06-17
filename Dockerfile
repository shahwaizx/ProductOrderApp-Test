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

# Copy only deps first for caching
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy in your entire test suite
COPY . .

# Run the single‐file test suite
# NOTE: this must match the actual filename (test.py)
CMD ["python", "test.py", "-v"]
