if [ "$1" == "-b" ]; then
	cd scripts
	./build.sh
	cd ..
fi
python3 webapp.py

