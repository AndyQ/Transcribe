#!/bin/bash

# It creates the virtual environment and installs the python dependancies
#
# It will then create the data folders to hold waiting, inprogress 
# and completed files, the instance folder and creates the
# sqlite database
#
# It will also download the Whisper models
#
# It will then give instuctions on how to setup the other bits

# Check python
# !/bin/bash
if which python > /dev/null 2>&1; then
    echo "python is installed"
else
    echo "python is not installed"
    exit 1
fi

ver=$(python -c"import sys; print(sys.version_info.major)")
if [ "$ver" -ne 3 ]; then
    echo "Unknown or unsupported python version: $ver"
fi


# Create and activate virtual environment, upgrade pip and install dependancies
if [ ! -d "./venv" ]; then
    python3 -m venv venv
fi
. ./venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create data folders and sqlite database
if [ ! -d "./data" ]; then
    mkdir ./data ./data/waiting ./data/inprogress ./data/done  instance
fi

if [ ! -d "./3rdparty" ]; then
    mkdir ./3rdparty ./3rdparty/models
fi

python3 -m scripts.init-db

# Download the Whisper base model
if [ ! -f "./3rdparty/ggml-$model.bin" ]; then
    src="https://huggingface.co/datasets/ggerganov/whisper.cpp"
    pfx="resolve/main/ggml"
    model="base"
    if [ -x "$(command -v wget)" ]; then
        wget --quiet --show-progress -O 3rdparty/models/ggml-$model.bin $src/$pfx-$model.bin
    elif [ -x "$(command -v curl)" ]; then
        curl -L --output 3rdparty/models/ggml-$model.bin $src/$pfx-$model.bin
    else
        printf "Either wget or curl is required to download models.\n"
        exit 1
    fi

    if [ $? -ne 0 ]; then
        printf "Failed to download ggml model %s\n" "$model"
        printf "Please try again later or download the original Whisper model files and convert them yourself.\n"
        exit 1
    fi
fi

echo "The base model has been installed.  If you wish to use other models please see https://github.com/ggerganov/whisper.cpp"
echo ""
echo "You need to download and install ffmpeg andwhisper.cpp"
