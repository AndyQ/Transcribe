cd client
npm run serve & pid1="$!" 

cd ../server
. ./venv/bin/activate
python main.py

kill $pid1


