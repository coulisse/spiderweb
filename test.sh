if [ "$1" == "-b" ]; then
	cd scripts || exit
	./build.sh
	cd ..
fi
#python3 webapp.py
flask --app webapp.py run

