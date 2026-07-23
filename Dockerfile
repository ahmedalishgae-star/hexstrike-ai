FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system packages including security tools available in Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    gcc \
    libpq-dev \
    git \
    unzip \
    make \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    libpcap-dev \
    # Network & Recon tools
    nmap \
    masscan \
    dnsutils \
    iputils-ping \
    netcat-openbsd \
    whois \
    # Web App Security tools
    gobuster \
    dirb \
    sqlmap \
    # Recon tools
    fierce \
    dnsenum \
    # Auth tools
    hydra \
    john \
    hashcat \
    medusa \
    # Binary analysis
    binwalk \
    exiftool \
    foremost \
    steghide \
    # Forensics
    sleuthkit \
    nuclei \
    # Utilities
    jq \
    yq \
    tmux \
    vim \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python-based tools
RUN pip install --no-cache-dir \
    wfuzz \
    arjun \
    x8 \
    dirsearch \
    prowler \
    checkov \
    pwntools \
    mitmproxy \
    selenium \
    webdriver-manager \
    undetected-chromedriver \
    beautifulsoup4 \
    lxml \
    aiohttp \
    fastmcp \
    flask \
    psutil \
    requests \
    python-dotenv

# Install nuclei templates (using nuclei from apt)
RUN nuclei -update-templates 2>/dev/null || true

# Install Chrome for Selenium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install rustscan
RUN wget -q https://github.com/RustScan/RustScan/releases/download/2.0.1/rustscan_2.0.1_amd64.deb -O /tmp/rustscan.deb && \
    dpkg -i /tmp/rustscan.deb && \
    rm /tmp/rustscan.deb

# Install evil-winrm
RUN gem install evil-winrm 2>/dev/null || true

# Create directories
RUN mkdir -p /app/data /app/logs /app/tools

WORKDIR /app

COPY hexstrike_server.py .
COPY hexstrike_mcp.py .
COPY requirements.txt .
COPY hexstrike-ai-mcp.json .

# Install only core requirements (skip heavy binary analysis deps)
RUN pip install --no-cache-dir \
    "flask>=2.3.0,<4.0.0" \
    "requests>=2.31.0,<3.0.0" \
    "psutil>=5.9.0,<6.0.0" \
    "fastmcp>=0.2.0,<1.0.0" \
    "beautifulsoup4>=4.12.0,<5.0.0" \
    "selenium>=4.15.0,<5.0.0" \
    "webdriver-manager>=4.0.0,<5.0.0" \
    "aiohttp>=3.8.0,<4.0.0" \
    "mitmproxy>=9.0.0,<11.0.0" \
    "pwntools>=4.10.0,<5.0.0" \
    bcrypt==4.0.1

EXPOSE 8888

ENV HEXSTRIKE_HOST=0.0.0.0
ENV HEXSTRIKE_PORT=8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

ENTRYPOINT ["python", "hexstrike_server.py"]