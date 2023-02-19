cd client
npm run serve & pid1="$!" 

cd ../server
python main.py

kill $pid1


