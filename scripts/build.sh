path_templates='../templates'
base_template='_base.html'
path_static_html='../static/html'

echo '*** SPIDERWEB  building process ***'
echo 'get version from git'
ver=`git tag|tail -1`
if [ "$?" != "0" ]; then
	echo 'ERROR on get version from git'
	exit 1
fi
if [ ${ver} == "" ]; then
	echo 'ERROR git version is empty'
	exit 1
fi
echo 'version: '${ver}

echo 'writing version in '${base_template} '...'
sed -i 's/<span id="version">v.*<\/span>/<span id="version">'$ver'<\/span>/g' ${path_templates}/${base_template}
if [ "$?" != "0" ]; then
	echo 'ERROR writing version in '${base_template} 
	exit 1
fi

echo 'generating static pages...'
staticjinja build --srcpath=${path_static_html}/templates/ --outpath=${path_static_html}/
if [ "$?" != "0" ]; then
	echo 'ERROR generating static pages'                
	exit 1
fi
