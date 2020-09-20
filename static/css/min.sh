#used to minify the css                                               
for i in `ls -1 *.css`
do
	echo ${i}
        file_no_ext="${i%.css}"
	curl -X POST --data-urlencode 'input@'${i}  https://cssminifier.com/raw > min/${file_no_ext}.min.css
done
