#!/bin/bash
#-------------------------------------------------------------
# script for creating a test database
#-------------------------------------------------------------

chr() {
    local ascii=$(echo $1 | awk '{ printf("%c",$0); }')
    echo ${ascii}
}

db_insert () {
    n=2000000
    for (( i=1; i<=${n}; i++ ))
    do
        freq=$(shuf -i 100-50000 -n 1)
        spotdxcc=$(shuf -i 1-500 -n 1)
        spotterdxcc=$(shuf -i 1-500 -n 1)
        spotitu=$(shuf -i 1-90 -n 1)
        spotcq=$(shuf -i 1-40 -n 1)
        spotteritu=$(shuf -i 1-90 -n 1)
        spottercq=$(shuf -i 1-40 -n 1)
        #for epoc use https://www.epochconverter.com/
        
        curr_epoch_time=$(date +%s)
        #timestamp=$(shuf -i 1673759569-1673763169 -n 1)
        #epoch_start=$((${curr_epoch_time}-3600*24*365*2))
        epoch_start=$((${curr_epoch_time}-3600))
        #echo ${curr_epoch_time}
        #echo ${epoch_start}
        timestamp=$(shuf -i ${epoch_start}-${curr_epoch_time} -n 1)

        cs_letter_1=$(chr $(shuf -i 65-90 -n1))
        cs_letter_2=$(chr $(shuf -i 65-90 -n1))
        cs_number=$(shuf -i 1-2 -n 1)
        callsign=${cs_letter_1}${cs_letter_2}${cs_number}DUMMY
        #callsign=IU1BDX

        #current timestamp
        #sudo mysql -uroot dxcluster -e "INSERT INTO spot VALUES (${i},${freq},'IU1BOX',UNIX_TIMESTAMP(),'DUMMY TEST','IU1BOW',${spotdxcc},${spotterdxcc},'IU1BOW-2',${spotitu},${spotcq},${spotteritu},${spottercq},NULL,NULL,'5.198.229.129');"
        #using random timestamp
        
        sudo mysql -uroot dxcluster -e "INSERT INTO spot VALUES (${i},${freq},'${callsign}',${timestamp},'DUMMY TEST','IU1BOW',${spotdxcc},${spotterdxcc},'IU1BOW-2',${spotitu},${spotcq},${spotteritu},${spottercq},NULL,NULL,'5.198.229.129');"
        #sudo mysql -uroot dxcluster -e "INSERT INTO spot VALUES (${i},${freq},'${callsign}',UNIX_TIMESTAMP(),'DUMMY TEST','IU1BOW',${spotdxcc},${spotterdxcc},'IU1BOW-2',${spotitu},${spotcq},${spotteritu},${spottercq},NULL,NULL,'5.198.229.129');"
        sleep 3
        p=$(( ${i}*100/${n} ))
      #  echo -ne ${p}'% \r'
    done

   # echo -ne '\n'
}


bold=$(tput bold)
normal=$(tput sgr0)

echo "${bold}WARNING${normal}: this command will drop your dxcluster database"
echo "Run it only on test environment!!!"

while true; do
    read -p "Would you procede? " yn
    case $yn in
        [Yy]* ) sudo mysql -uroot  <dxcluster_schema_for_test.sql;db_insert;break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done


