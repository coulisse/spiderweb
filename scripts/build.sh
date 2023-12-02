#! /bin/bash
#***********************************************************************************
# Script used to BUILD the progect (ie. replacing version, minify etc) 
#***********************************************************************************
path_templates='../templates'
base_template='_base.html'
path_static='../static'
path_static_html=${path_static}'/html'
path_static_js=${path_static}'/js'
path_static_css=${path_static}'/css'
path_static_pwa=${path_static}'/pwa'
path_cfg='../cfg'
app_ini=${path_cfg}'/webapp_log_config.ini'
path_docs='../docs'
readme='../README.md'
changelog=${path_docs}'/'CHANGELOG.md
citation='../CITATION.cff'
sw=${path_static_pwa}'/service-worker.js'

html_change_references(){
	for i in ${path_templates}/*.html
	do
		echo "changing references to scripts in ${i}"
		if [ "${1}" == "-r" ]; then
			# concatenating 2 sed command with ";"
			# 1) if found static/js/dev/ replace .js with .min.js
			# 2) replace static/js/dev/ with static/js/rel/
			if ! sed -i '/static\/js\/dev/s/\.js/\.min\.js/;s/static\/js\/dev/static\/js\/rel/g' ${i}; then               
				echo 'ERROR replacing .js to .min.js '
				exit 6
			fi
			# the same but for css
			if ! sed -i '/static\/css\/dev/s/\.css/\.min\.css/;s/static\/css\/dev/static\/css\/rel/g' ${i}; then               
				echo 'ERROR  replacing .css to .min.css '
				exit 6
			fi	

		elif [ "${1}" == "-d" ]; then
			# concatenating 2 sed command with ";"
			# 1) if found static/js/rel/ replace .min.js with .js
			# 2) replace static/js/rel/ with static/js/dev/		
			if ! sed -i '/static\/js\/rel/s/\.min\.js/\.js/;s/static\/js\/rel/static\/js\/dev/g' ${i}; then               
				echo 'ERROR  replacing .min.js to .js'
				exit 6
			fi
			# the same but for css
			if ! sed -i '/static\/css\/rel/s/\.min\.css/\.css/;s/static\/css\/rel/static\/css\/dev/g' ${i}; then               
				echo 'ERROR  replacing .min.css to .css'
				exit 6
			fi		

		fi
	done
}

if [ "$1" != "-r" ] && [ "$1" != "-d" ]; then
	echo 'wrong options for first parameter. Options permitted:'
	echo '   -d: debug'
	echo '   -r: release'
	exit 5
fi

if [ "$2" != "-c" ]  && [ "$2" != "" ]; then
	echo 'wrong options for second parameter. Option permitted:'
	echo '   -c: commit'
	exit 5
fi


echo '*** SPIDERWEB  building process ***'
if [ "$1" == "-r" ]; then
	echo 'creating RELEASE application'

	#used to minify the application javascript                            
	echo 'minify javascripts...'
	shopt -s extglob
	rm ${path_static_js}/rel/*.js
	for i in ${path_static_js}/dev/*.js
	do
		[[ -e ${i} ]] || break  # handle the case of no files found
		file_no_ext=$(basename "${i%.js}")
		out=${path_static_js}/rel/${file_no_ext}.min.js
		echo "${i} --> ${out}"
		if ! uglifyjs --compress --mangle  -- ${i} > ${out}
		then                            
			echo 'ERROR minifying javascript: '${i}          
			shopt -u extglob
			exit 80
		fi
		if [ ! -s "${out}" ]; then
			echo "File is empty"
			shopt -u extglob
			exit 81
		fi
	done


	#used to minify css                            
	echo 'minify css...'
	rm ${path_static_css}/rel/*.css
	for i in ${path_static_css}/dev/*.css
	do
		[[ -e ${i} ]] || break  # handle the case of no files found
		echo ${i}
		file_no_ext=$(basename "${i%.css}")
		out=${path_static_css}/rel/${file_no_ext}.min.css
		echo "${i} --> ${out}"
		#if ! curl -X POST -s --fail --compressed --data "code_type=css"  --data-urlencode 'code@'${i} https://htmlcompressor.com/compress  > ${path_static_css}/rel/${file_no_ext}.min.css
		if ! css-minify -f ${i} -o ${path_static_css}/rel/
		then
			echo 'ERROR minifying css: ' ${out}          
			shopt -u extglob
			exit 90
		fi
		if [ ! -s "${out}" ]; then
			echo "File is empty"
			shopt -u extglob
			exit 91
		fi	
		#sleep 5
	done
	shopt -u extglob
	html_change_references -r

	echo 'writing requirements...'
	if ! pip freeze|tee ../requirements.txt
	then                           
		echo 'ERROR wrinting requirements'                
		exit 60
	fi

	echo 'remove some packages from requirements...'
	sed -i '/certifi==/d' ../requirements.txt
	sed -i '/staticjinja==/d' ../requirements.txt
	sed -i '/lighthouse==/d' ../requirements.txt

	echo 'force some requirements...'
	sed -i 's/mysql-connector-python==8.0.31/mysql-connector-python>=8.0.31/' ../requirements.txt
	sed -i 's/mysql-connector-python==8.2.0/mysql-connector-python>=8.2.0/' ../requirements.txt

	if ! sed -i '7,25s/level=DEBUG/level=INFO/g' ${app_ini}; then               
		echo 'ERROR settimg loglevel=INFO '
		exit 12
	fi
fi

if [ "$1" == "-d" ]; then
	echo 'creating DEBUG application'
	html_change_references -d

	if ! sed -i '7,25s/level=INFO/level=DEBUG/g' ${app_ini}; then               
		echo 'ERROR settimg loglevel=DEBUG '
		exit 12
	fi

fi


#echo 'create modes.json from dxspider bands.pl'

#python ../lib/get_dxcluster_modes.py /home/sysop/spider/data/bands.pl
#if [ "$?" != "0" ]; then
#	echo 'ERROR on creating modes.json from dxspider bands.pl'
#	exit 5
#fi

echo 'get version from version.txt'
#if ! ver=$(git describe --tags --abbrev=0)
#if ! ver=$(git tag|tail -1)
if ! ver=$(head -1 ../cfg/version.txt)
then
	echo 'ERROR on get version'
	exit 10
fi

if [ ${ver} == "" ]; then
	echo 'ERROR version is empty'
	exit 20
fi
echo 'version: '${ver}

echo 'writing version in '${path_static_pwa}/manifest.webmanifest '...'
if ! sed -i 's/v.*",/'$ver'",/g' ${path_static_pwa}/manifest.webmanifest
then                      
	echo 'ERROR writing version in '${path_static_pwa}/manifest.webmanifest
	exit 42
fi

echo 'writing version in '${readme} '...'
if ! sed -i  's/- \*\*Release:\*\* v.*/- \*\*\Release:\*\* '$ver'/g' ${readme}
then
	echo 'ERROR writing version in '${readme} 
	exit 30
fi

echo 'writing version in '${changelog} '...'
if ! sed -i '1,4s/Release: v.*/Release: '$ver'/g' ${changelog}
then                           
	echo 'ERROR writing version in '${changelog}
	exit 35
fi

echo 'writing date in '${changelog} '...'
if ! sed -i  '1,4s/Date: [0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]/Date: '$(date '+%d\/%m\/%Y')'/g'  ${changelog}
then                            
	echo 'ERROR writing date in '${changelog}
	exit 35
fi


echo 'writing version in '${citation} '...'
if ! sed -i '2,99s/version: v.*/version: '$ver'/g' ${citation}
then                           
	echo 'ERROR writing version in '${citation}
	exit 35
fi

echo 'writing date in '${citation} '...'
if ! sed -i  '2,99s/date-released: [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/date-released: '$(date '+%Y-%m-%d')'/g'  ${citation}
then                            
	echo 'ERROR writing date in '${citation}
	exit 35
fi


echo 'writing version in '${base_template} '...'
if ! sed -i 's/<span id="version">v.*<\/span>/<span id="version">'$ver'<\/span>/g' ${path_templates}/${base_template}
then                          
	echo 'ERROR writing version in '${base_template} 
	exit 40
fi

echo 'writing version in '${sw} '...'

if ! sed -i  's/pwa-spiderweb_v.*/pwa-spiderweb_'$ver'\x27/g'  ${sw}
then                            
	echo 'ERROR writing date in '${sw}
	exit 35
fi

echo "changing references to scripts in ${sw}"
if [ "${1}" == "-r" ]; then
	# concatenating 2 sed command with ";"
	# 1) if found static/js/dev/ replace .js with .min.js
	# 2) replace static/js/dev/ with static/js/rel/
	if ! sed -i '/static\/js\/dev/s/\.js/\.min\.js/;s/static\/js\/dev/static\/js\/rel/g' ${sw}; then               
		echo 'ERROR replacing .js to .min.js in ' ${sw}
		exit 6
	fi
	# the same but for css
	if ! sed -i '/static\/css\/dev/s/\.css/\.min\.css/;s/static\/css\/dev/static\/css\/rel/g' ${sw}; then               
		echo 'ERROR  replacing .css to .min.css in ' ${sw}
		exit 6
	fi	

elif [ "${1}" == "-d" ]; then
	# concatenating 2 sed command with ";"
	# 1) if found static/js/rel/ replace .min.js with .js
	# 2) replace static/js/rel/ with static/js/dev/		
	if ! sed -i '/static\/js\/rel/s/\.min\.js/\.js/;s/static\/js\/rel/static\/js\/dev/g' ${sw}; then               
		echo 'ERROR  replacing .min.js to .js in ' ${sw}
		exit 6
	fi
	# the same but for css
	if ! sed -i '/static\/css\/rel/s/\.min\.css/\.css/;s/static\/css\/rel/static\/css\/dev/g' ${sw}; then               
		echo 'ERROR  replacing .min.css to .css in ' ${sw}
		exit 6
	fi		

fi

echo Build ok

if [ "$2" == "-c" ]; then
	if [ "$1" == "-r" ]; then
		echo '*** SPIDERWEB  commit process ***'

		head -10 ../docs/CHANGELOG.md

		read -p "Do you want to proceed to commit version ${ver} (yes/no) " yn

		case $yn in 
			yes ) echo ok, we will proceed;;
			y ) echo ok, we will proceed;;
			no ) echo exiting...;
				exit;;
			n ) echo exiting...;
				exit;;
			* ) echo invalid response;
				exit 1;;
		esac


		if ! git add --all ; then
			echo 'Error on adding files'
			exit 7
		fi		
		
		echo 'Please, add comment for commit on tag ' ${ver}
		read comm_tag_msg
		if ! git commit -m "${comm_tag_msg}"; then
			echo 'Error on commit'
			exit 9
		fi			
		echo Commit ok

		if ! git tag ${ver} HEAD -m "${comm_tag_msg}"; then
			echo 'Error on tagging'
			exit 8
		fi			
		echo Tagging ok
		echo If you would to push execute this command:
		echo git push --atomic origin development ${ver}
	else
		echo 'Error: You can make a commit only if the first option is -r = release!!!'
		exit 10
	fi
fi


echo

#git push --atomic origin development v2.4.5.71