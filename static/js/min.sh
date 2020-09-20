#used to minify the application javascript                            
for i in `ls -1 *.js`
do
	echo ${i}
        file_no_ext="${i%.js}"
	curl -X POST --data-urlencode 'input@'${i} https://javascript-minifier.com/raw > min/${file_no_ext}.min.js
done

