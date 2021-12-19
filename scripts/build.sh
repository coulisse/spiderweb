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

echo '*** SPIDERWEB  building process ***'
echo 'get version from git'
ver=`git describe --tags --abbrev=0`
if [ "$?" != "0" ]; then
	echo 'ERROR on get version from git'
	exit 10
fi
if [ ${ver} == "" ]; then
	echo 'ERROR git version is empty'
	exit 20
fi
echo 'version: '${ver}

echo 'writing version in '${manifest} '...'
sed -i 's/v.*",/'$ver'",/g' ${manifest}
if [ "$?" != "0" ]; then
	echo 'ERROR writing version in '${manifest} 
	exit 420
fi

echo 'writing version in '${readme} '...'
sed -i  's/- \*\*Release:\*\* v.*/- \*\*\Release:\*\* '$ver'/g' ${readme}
if [ "$?" != "0" ]; then
	echo 'ERROR writing version in '${readme} 
	exit 30
fi

echo 'writing version in '${changelog} '...'
sed -i  '1,4s/Release: v.*/Release: '$ver'/g' ${changelog}
if [ "$?" != "0" ]; then
	echo 'ERROR writing version in '${changelog}
	exit 35
fi

echo 'writing date in '${changelog} '...'
sed -i  '1,4s/Date: [0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]/Date: '`date '+%d\/%m\/%Y'`'/g'  ${changelog}
if [ "$?" != "0" ]; then
	echo 'ERROR writing date in '${changelog}
	exit 35
fi

echo 'writing version in '${base_template} '...'
sed -i 's/<span id="version">v.*<\/span>/<span id="version">'$ver'<\/span>/g' ${path_templates}/${base_template}
if [ "$?" != "0" ]; then
	echo 'ERROR writing version in '${base_template} 
	exit 40
fi

echo 'generating static pages...'
#staticjinja build --srcpath=${path_static_html}/templates/ --outpath=${path_static_html}/ --log=info
python ../lib/static_build.py
if [ "$?" != "0" ]; then
	echo 'ERROR generating static pages'                
	exit 50
fi

echo 'writing requirements...'
pip freeze|tee ../requirements.txt
if [ "$?" != "0" ]; then
	echo 'ERROR wrinting requirements'                
	exit 60
fi

#used to minify the application javascript                            
echo 'minify javascripts...'
for i in `ls -1 ${path_static_js}/ -I "*.min.*" -I "*.md"`
do
	echo ${i}
    file_no_ext=`basename "${i%.js}"`
	#curl -X POST --data-urlencode 'input@'${path_static_js}/${i} https://javascript-minifier.com/raw > ${path_static_js}/${file_no_ext}.min.js
	curl -X POST -s --data-urlencode 'input@'${path_static_js}/${i} https://www.toptal.com/developers/javascript-minifier/raw > ${path_static_js}/${file_no_ext}.min.js
	if [ "$?" != "0" ]; then
		echo 'ERROR minifying javascript: '${i}          
		exit 80
	fi
	sleep 3
done

#used to minify css                            
echo 'minify css...'
for i in `ls -1 ${path_static_css}/ -I "*.min.*" -I "*.md"`
do
	echo ${i}
    file_no_ext=`basename "${i%.css}"`
	curl -X POST --data-urlencode 'input@'${path_static_css}/${i} https://cssminifier.com/raw > ${path_static_css}/${file_no_ext}.min.css
	if [ "$?" != "0" ]; then
		echo 'ERROR minifying css: '${i}          
		exit 80
	fi
	sleep 3
done

echo
echo Build ok
