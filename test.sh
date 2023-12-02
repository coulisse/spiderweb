if [ $# -gt 0 ]
  then
	cd scripts || exit
	if ! ./build.sh ${1}
	then
		cd ..
		echo "terminated"
		exit 1
	fi
	cd ..
fi

if [ "$1" == "-d" ]; then
        rm -rf __pycache__
	flask --app webapp.py --debug run --exclude-patterns *webapp.log*
else
	flask --app webapp.py run 
fi




