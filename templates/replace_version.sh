make_replace() {
	for i in `ls -1 *.html`
		do
			cp ${i} ${i}.old
#replace css
			sed -i 's/5.0.0/5.0.2/g' ${i}
			sed -i 's/sha384-wEmeIV1mKuiNpC+IOBjI7aAzPcEZeedi5yW5f2yOq55WWLwNGmvvx4Um1vskeMj0/sha384-EVSTQN3\/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC/g' ${i}
            sed -i 's/sha384-p34f1UUtsS3wqzfto5wAAmdvj+osOnFyQFpp4Ua3gs\/ZVWx6oOypYoCJhGGScy+8/sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn\/tWtIaxVXM/g' ${i}

#replace js
    	    #sed -i 's/sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf/sha384-p34f1UUtsS3wqzfto5wAAmdvj+osOnFyQFpp4Ua3gs\/ZVWx6oOypYoCJhGGScy+8/g' ${i}
			echo ${i}
            #sed -i 's/"https:\/\/code.jquery.com\/jquery-3.5.1.slim.min.js" integrity="sha256-4+XzXVhsDmqanXGHaHvgh1gMQKX40OUvDEBTu8JcmNs="/https:"\/\/cdnjs.cloudflare.com\/ajax\/libs\/jquery\/3.6.0\/jquery.slim.min.js" integrity="sha512-6ORWJX\/LrnSjBzwefdNUyLCMTIsGoNP6NftMy2UAm1JBm6PRZCO1d7OHBStWpVFZLO+RerTvqX\/Z9mBFfCJZ4A=="/g' ${i}
            sed -i 's/"https:\/\/cdnjs.cloudflare.com\/ajax\/libs\/jquery\/3.6.0\/jquery.slim.min.js" integrity="sha512-6ORWJX\/LrnSjBzwefdNUyLCMTIsGoNP6NftMy2UAm1JBm6PRZCO1d7OHBStWpVFZLO+RerTvqX\/Z9mBFfCJZ4A=="/https:\/\/cdnjs.cloudflare.com\/ajax\/libs\/jquery\/3.6.0\/jquery.slim.js" integrity="sha512-6ORWJX\/LrnSjBzwefdNUyLCMTIsGoNP6NftMy2UAm1JBm6PRZCO1d7OHBStWpVFZLO+RerTvqX\/Z9mBFfCJZ4A=="/g' ${i}
	done
}


echo WARNING
echo This script will replace the version of bootrstrap CSS an JS
echo use it only if you know what you are doing
echo
while true; do
    read -p "Do you wish to proceed?" yn
    case $yn in
        [Yy]* ) make_replace; break;;
        [Nn]* ) exit;;
	    * ) echo "Please answer yes or no.";;
    esac
done
