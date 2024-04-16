# Build whisper
FROM python:3.11-slim-bookworm as builder
RUN apt-get clean && apt-get update && \
    apt-get -qy install git g++ make wget

WORKDIR /app

COPY --from=mwader/static-ffmpeg:6.1.1 /ffmpeg /ffmpeg   

RUN ls -la /


RUN git clone https://github.com/ggerganov/whisper.cpp.git /whisper.cpp &&\
    cd /whisper.cpp && uname -m && make main


FROM python:3.11-slim-bookworm

RUN apt-get clean && apt-get update &&\
    apt-get -qy install wget


RUN bash -c 'mkdir -pv data/{waiting,inprogress,done} instance 3rdparty/models' &&\
    pip3 install --upgrade pip &&\
    wget  --quiet --show-progress -O 3rdparty/models/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true

COPY --from=builder /whisper.cpp/main ./3rdparty/whisper

# RUN cp /whisper.cpp/main ./3rdparty/whisper && cp /ffmpeg ./3rdparty/ffmpeg


COPY --from=builder /ffmpeg ./3rdparty/ffmpeg

COPY . ./ 
RUN pip3 install -r requirements.txt
RUN python3 -m scripts.init-db

EXPOSE 8080:8080
CMD ["./run.sh"]

