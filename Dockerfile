# Build whisper
FROM python:3.10-slim-bullseye as builder
RUN apt-get clean && apt-get update &&\
    apt-get -qy install git g++ make

COPY --from=mwader/static-ffmpeg:5.1.2-arm64 /ffmpeg /ffmpeg    

RUN git clone https://github.com/ggerganov/whisper.cpp.git &&\
    cd whisper.cpp && make


FROM python:3.10-slim-bullseye

RUN apt-get clean && apt-get update &&\
    apt-get -qy install wget

WORKDIR /app

RUN bash -c 'mkdir -pv data/{waiting,inprogress,done} instance 3rdparty/models' &&\
    pip3 install --upgrade pip &&\
    wget  --quiet --show-progress -O 3rdparty/models/ggml-base.bin https://huggingface.co/datasets/ggerganov/whisper.cpp/resolve/main/ggml-base.bin

COPY --from=builder /whisper.cpp/main ./3rdparty/whisper

COPY --from=builder /ffmpeg ./3rdparty/ffmpeg

COPY . ./
RUN pip3 install -r requirements.txt
RUN python3 -m scripts.init-db

EXPOSE 8080:8080
CMD ["./run.sh"]

