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
path_docs='../docs'
readme='../README.md'
manifest=${path_static}'/manifest.webmanifest'
changelog=${path_docs}'/'CHANGELOG.md

#echo '*** SPIDERWEB  building process ***'
#echo 'create modes.json from dxspider bands.pl'
#python ../lib/get_dxcluster_modes.py /home/sysop/spider/data/bands.pl
#if [ "$?" != "0" ]; then
#	echo 'ERROR on creating modes.json from dxspider bands.pl'
#	exit 5
#fi

echo 'get version from git'
#ver=`git describe --tags --abbrev=0`
if ! ver=$(git describe --tags --abbrev=0)
then
	echo 'ERROR on get version from git'
	exit 10
fi
if [ ${ver} == "" ]; then
	echo 'ERROR git version is empty'
	exit 20
fi
echo 'version: '${ver}

echo 'writing version in '${manifest} '...'
if ! sed -i 's/v.*",/'$ver'",/g' ${manifest}
then                      
	echo 'ERROR writing version in '${manifest} 
	exit 42
fi

echo 'writing version in '${readme} '...'
if ! sed -i  's/- \*\*Release:\*\* v.*/- \*\*\Release:\*\* '$ver'/g' ${readme}
then
	echo 'ERROR writing version in '${readme} 
	exit 30
fi

echo 'writing version in '${changelog} '...'
if ! sed -i  '1,4s/Release: v.*/Release: '$ver'/g' ${changelog}
then                           
	echo 'ERROR writing version in '${changelog}
	exit 35
fi

echo 'writing date in '${changelog} '...'
#sed -i  '1,4s/Date: [0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]/Date: '`date '+%d\/%m\/%Y'`'/g'  ${changelog}
if ! sed -i  '1,4s/Date: [0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]/Date: '$(date '+%d\/%m\/%Y')'/g'  ${changelog}
then                            
	echo 'ERROR writing date in '${changelog}
	exit 35
fi

echo 'writing version in '${base_template} '...'
if ! sed -i 's/<span id="version">v.*<\/span>/<span id="version">'$ver'<\/span>/g' ${path_templates}/${base_template}
then                          
	echo 'ERROR writing version in '${base_template} 
	exit 40
fi

echo 'generating static pages...'
#staticjinja build --srcpath=${path_static_html}/templates/ --outpath=${path_static_html}/ --log=info
if ! python ../lib/static_build.py
then                               
	echo 'ERROR generating static pages'                
	exit 50
fi

echo 'writing requirements...'
if ! pip freeze|tee ../requirements.txt
then                           
	echo 'ERROR wrinting requirements'                
	exit 60
fi

#used to minify the application javascript                            
echo 'minify javascripts...'
shopt -s extglob
for i in ${path_static_js}/!(*[m][i][n].js|*.md)
do
    [[ -e ${i} ]] || break  # handle the case of no files found
	echo ${i}
    file_no_ext=$(basename "${i%.js}")
	if ! curl -X POST -s --data-urlencode 'input@'${i} https://www.toptal.com/developers/javascript-minifier/raw > ${path_static_js}/${file_no_ext}.min.js
	then                            
		echo 'ERROR minifying javascript: '${i}          
		shopt -u extglob
		exit 80
	fi
	sleep 3
done

#used to minify css                            
echo 'minify css...'
for i in ${path_static_css}/!(*[m][i][n].css|*.md)
do
    [[ -e ${i} ]] || break  # handle the case of no files found
	echo ${i}
    file_no_ext=$(basename "${i%.css}")
	#curl -X POST --data-urlencode 'input@'${path_static_css}/${i} https://cssminifier.com/raw > ${path_static_css}/${file_no_ext}.min.css
	if ! curl -X POST --data-urlencode 'input@'${i} https://cssminifier.com/raw > ${path_static_css}/${file_no_ext}.min.css
	then
		echo 'ERROR minifying css: '${i}          
		shopt -u extglob
		exit 80
	fi
	sleep 3
done
shopt -u extglob
echo
echo Build ok
