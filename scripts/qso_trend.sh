DIR=`realpath -s $0|sed 's|\(.*\)/.*|\1|'`  
echo Absolute path: ${DIR}
cd ${DIR} 
python3 qso_trend.py

