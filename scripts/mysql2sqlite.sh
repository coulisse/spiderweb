
#!/bin/bash
echo this script will convert your mysql db to sqllite databases


#TODO: 
#
# read dxvars
# check sqllite perl
# dump mysql
# create table in sqlite
# import in sqlite
# create indexes
# change dxvars.pm
# 

sqlite_db=dxcluster.db 
mysql_dump_db=$(mktemp) 
mysql_dump_db="mysql.sql"   #TODO: remove

progress_bar() {
    local width=50
    local percent="$1"
    local filled_width=$((width * percent / 100))
    local dots="$(printf '%*s' "$filled_width" | tr ' ' '=')"
    local spaces="$(printf '%*s' "$((width - filled_width))" | tr ' ' ' ')"
    echo -ne "[$dots$spaces] ($percent%)\r"
}


#Empty database
if ! >  ${sqlite_db}; 
  then
    echo 'Error empting sqlite db: ' ${sqlite_db}
  exit 1
else
    echo 'sqlite db created: ' ${sqlite_db}
fi

#dump mysql data
#TODO: remove comments
#read -p 'MySQL User: ' user
#
#if ! mysqldump -u ${user} -p --skip-create-options  --compatible=ansi --skip-extended-insert  --compact --single-transaction  --databases dxcluster \
#  | grep "INSERT INTO" \
#  | sed -e ':a' -e 'N' -e '$!ba' -e 's/,\n)/\n)/'\
#  | sed -e 's/\\'\''/'\'''\''/g'\
#  > ${mysql_dump_db}; 
#  then
#	    echo 'Error on dumping mysql data'
#        exit 1
#  else
#        echo 'dump created: ' ${mysql_dump_db}
#fi		

#create table spot
if ! sqlite3 ${sqlite_db} <<EOF
CREATE TABLE "spot" (
  "rowid" INTEGER PRIMARY KEY,
  "freq" REAL NOT NULL,
  "spotcall" TEXT NOT NULL,
  "time" INTEGER NOT NULL,
  "comment" TEXT DEFAULT NULL,
  "spotter" TEXT NOT NULL,
  "spotdxcc" INTEGER DEFAULT NULL,
  "spotterdxcc" INTEGER DEFAULT NULL,
  "origin" TEXT DEFAULT NULL,
  "spotitu" INTEGER DEFAULT NULL,
  "spotcq" INTEGER DEFAULT NULL,
  "spotteritu" INTEGER DEFAULT NULL,
  "spottercq" INTEGER DEFAULT NULL,
  "spotstate" TEXT DEFAULT NULL,
  "spotterstate" TEXT DEFAULT NULL,
  "ipaddr" TEXT DEFAULT NULL
);
EOF
  then
    echo 'Error on creating table spot in Sqlite'
    exit 1
  else
    echo 'Table spot created in sqlite db: ' ${sqlite_db}
fi

#import spot in sqlite
max_insert=$(wc -l ${mysql_dump_db}|cut -d ' ' -f1)
echo 'Importing dump into Sqlite' ${max_insert} 'rows: '

counter=0
sv_perc=-1
while IFS= read -r line; do
    let "counter++"
    if ! sqlite3 ${sqlite_db} "${line}";
      then 
        echo '...at line: ' ${counter} ' | ' ${line}
    fi
    perc=$((   ${counter} * 100 / ${max_insert}  ))
    if [ ${perc} -ne ${sv_perc} ]; then
      sv_perc=${perc}
      progress_bar ${perc}
    fi
done < ${mysql_dump_db}

echo 'Sqlite db imported: ' ${sqlite_db}


#create index 
echo 'Creating indexes...'
if ! sqlite3 ${sqlite_db} <<EOF
CREATE INDEX idx_spot_spotcall ON spot (spotcall);
CREATE INDEX idx_spot_spotter ON spot (spotter);
EOF
  then
    echo 'Error on creating indexes on spot in Sqlite'
    exit 1
  else
    echo 'Indexes created in sqlite db: ' ${sqlite_db}
fi



exit  #TODO: remove exit
#remove dump file
rm ${mysql_dump_db}; 

echo done

