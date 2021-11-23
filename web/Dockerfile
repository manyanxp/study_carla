FROM ubuntu:bionic-20210930

RUN apt-get update && apt-get install -y wget openssh-server git vim iproute2

ARG user="myuser"
ARG homedir="/home/myuser"
1
RUN groupadd -r ${user} && useradd --no-log-init -r -g ${user} ${user}
WORKDIR ${homedir}
RUN chown -R ${user}:${user} ${homedir}

COPY ./PythonAPI ${homedir}/PythonAPI

USER ${user}

RUN pwd

ARG miniconda="Miniconda3-py37_4.9.2-Linux-x86_64.sh"
RUN wget https://repo.anaconda.com/miniconda/${miniconda} && \
    sh ${miniconda} -b -p ~/miniconda3 && \
    rm -f ${miniconda}

ENV PATH ${homedir}/miniconda3/bin:$PATH
RUN conda init

RUN conda create -n my_env python=3.7

RUN echo "export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0" >> ~/.bashrc

SHELL ["conda", "run", "-n", "my_env", "/bin/bash", "-c"]
RUN python -m pip install --upgrade pip
RUN pip install numpy matplotlib pandas pygame Django==3.1.7 djangorestframework==3.12.2 djangogrpcframework==0.2 grpcio==1.36.0 grpcio-tools==1.36.0  ./PythonAPI/carla-0.9.12-cp37-cp37m-manylinux_2_27_x86_64.whl

RUN echo "conda activate my_env" >> ~/.bashrc
