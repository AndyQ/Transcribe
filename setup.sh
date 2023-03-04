#!/bin/bash

# First setup the server
echo "Setting up server....."
cd server
./setup.sh
if [ $? -ne 0 ]; then
   echo "There were problems installing the server"
   exit 1
fi
cd ..

echo ""
echo "Please start the server using run.sh"
echo ""
echo "Then access using a web browser at http://localhost:8080"
