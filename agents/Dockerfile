FROM python:3.11-slim-bookworm

# Add git-lfs to apt
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash

# Update and install dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        software-properties-common sudo git-lfs wget apt-transport-https iputils-ping curl \
    && apt-get install -y tesseract-ocr poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Setup a non-root user 'autogen' with sudo access
RUN adduser --disabled-password --gecos '' autogen \
    && adduser autogen sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && groupadd -f docker \
    && usermod -aG docker autogen

USER autogen
WORKDIR /home/autogen

# Install mamba directly
USER root
RUN curl -L -o /tmp/mambaforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
    && bash /tmp/mambaforge.sh -b -p /home/autogen/mambaforge \
    && rm /tmp/mambaforge.sh \
    && /home/autogen/mambaforge/bin/mamba install --yes jupyter_kernel_gateway ipykernel matplotlib numpy \
    && /home/autogen/mambaforge/bin/mamba clean --all -f -y \
    && chown -R autogen:autogen /home/autogen/mambaforge

# Set environment variables for Mambaforge
ENV PATH="/home/autogen/mambaforge/bin:$PATH"
ENV TOKEN="UNSET"

USER autogen

# Install Python packages within the Mambaforge environment
RUN /home/autogen/mambaforge/bin/pip install --upgrade pip \
    && /home/autogen/mambaforge/bin/pip install pyautogen[teachable,lmm,retrievechat,mathchat,blendsearch] autogenra \
    && /home/autogen/mambaforge/bin/pip install numpy pandas matplotlib seaborn scikit-learn requests urllib3 nltk pillow pytest beautifulsoup4 \
    && /home/autogen/mambaforge/bin/pip install docker \
    && /home/autogen/mambaforge/bin/pip install pyautogen[jupyter-executor] \
    && /home/autogen/mambaforge/bin/pip install pyautogen \
    && /home/autogen/mambaforge/bin/pip install cryptography \
    && /home/autogen/mambaforge/bin/pip install unstructured[all-docs] \
    && /home/autogen/mambaforge/bin/pip install boto3  \
    && /home/autogen/mambaforge/bin/pip install pydantic==2.7.1

# Expose ports
EXPOSE 8081 8888

# Start Jupyter Kernel Gateway and Bash
CMD /home/autogen/mambaforge/bin/python -m jupyter kernelgateway \
    --KernelGatewayApp.ip=0.0.0.0 \
    --KernelGatewayApp.port=8888 \
    --KernelGatewayApp.auth_token=${TOKEN} \
    --JupyterApp.answer_yes=true \
    --JupyterWebsocketPersonality.list_kernels=true & \
    /bin/bash
