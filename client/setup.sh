#!/bin/bash

# Check node
if which npm > /dev/null 2>&1; then
    echo "node is installed"
else
    echo "node is not installed"
    exit 1
fi

npm install
if [ $? -ne 0 ]; then
    printf "Failed to install packages"
    exit 1
fi

echo "Client has been setup"
