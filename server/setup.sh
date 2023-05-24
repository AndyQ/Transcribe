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


# Check for FFMpeg
if which ffmpeg > /dev/null 2>&1; then
    echo "* FFMpeg is installed"
else
    echo "* FFMpeg is not installed - please download and install from https://ffmpeg.org/download.html then re-run setup"
    exit 1
fi


# Create and activate virtual environment, upgrade pip and install dependancies
echo "* setting up virtual environment...."
if [ ! -d "./venv" ]; then
    python3 -m venv venv
fi

if [ ! -d "./venv/bin/activate" ]; then
    . ./venv/bin/activate
    pip3 install --upgrade pip > /dev/null 2>&1 
    pip3 install -r requirements.txt > /dev/null
    if [ $? -ne 0 ]; then
        printf "Failed to install python dependancies\n"
        printf "Please try again later or install them manually.\n"
        exit 1
    fi
else
    echo "* Virtual environment is already setup"
fi

# Create data folders 
mkdir -p ./data ./data/waiting ./data/inprogress ./data/done ./data/export ./data/import  instance

# Create folder for 3rd party files
if [ ! -d "./3rdparty" ]; then
    mkdir ./3rdparty ./3rdparty/models
fi

# Create sqlite database
if [ ! -f "./instance/database.db" ]; then
    echo "* Creating database..."
    python3 -m scripts.init-db
fi

# Build whisper
if [ ! -f "./whisper.cpp" ]; then
    echo "* Building whisper.cpp...."
    git clone https://github.com/ggerganov/whisper.cpp.git > /dev/null 2>&1 
else
    cd ./whisper.cpp || exit
    git pull
    cd ..
fi

# Build whisper
cd ./whisper.cpp || exit
if ! make > /dev/null 2>&1 
then
    printf "Failed to build whisper.cpp\n"
    printf "Please try again later or build it yourself.\n"
    exit 1
fi
mv main ../3rdparty/whisper
cd ..

# Download the Whisper base model
if [ ! -f "./3rdparty/models/ggml-base.bin" ]; then
    echo "Downloading whisper base model"
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
echo "Please start the server using run.sh"
echo ""
echo "Then access using a web browser at http://localhost:8080"
