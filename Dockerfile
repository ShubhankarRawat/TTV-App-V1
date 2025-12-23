FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
LABEL maintainer="TheAI1"

# Install system deps (add patchelf/chromium if you still need them)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git git-lfs ffmpeg libsm6 libxext6 wget gnupg ca-certificates \
        chromium-driver xvfb x11-utils patchelf \
    && rm -rf /var/lib/apt/lists/*

# Use this as the single canonical WORKDIR so files are placed where the CMD expects them.
WORKDIR /home/user/app

# Copy only requirements first to leverage cache
COPY requirements.txt ./requirements.txt

# Install Python packages as root (so we can patch the .so files if needed)
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) patch ctranslate2 shared objects if you previously had the execstack error
# This tries to clear the execstack flag on libctranslate2 shared objects installed into site-packages.
RUN set -ex; \
    for prefix in /usr/local/lib/python*/site-packages /usr/lib/python*/site-packages; do \
      if [ -d "$prefix" ]; then \
        find "$prefix" -type f -name 'libctranslate2*.so*' -print -exec patchelf --clear-execstack {} \; || true; \
      fi; \
    done

# Copy application files into the canonical WORKDIR and set ownership to uid 1000 (we'll create the user later)
COPY --chown=1000:1000 . .

# Create non-root user that matches the uid used in the COPY above
RUN useradd -m -u 1000 user && chown -R user:user /home/user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

# Pre-download Gradio frpc (if you still want this)
RUN mkdir -p $HOME/.cache/huggingface/gradio/frpc && \
    wget -qO $HOME/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3 \
         https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64 && \
    chmod +x $HOME/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3

EXPOSE 7860

# final command: python will run app.py from /home/user/app
CMD ["python", "app.py"]
