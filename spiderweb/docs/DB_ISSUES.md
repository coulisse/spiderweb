#DX Spider database issue

If, after edit DXVars.pm, your DX Spider **not create mysql database**, you have to create it **manually**.
Before to run the below instructions, please check that the user which is used to run dxspider; I hope this is not root, but another user like "sysop". If you are running it with root, I think you could have some problems.                                                                                                                                                                                                        
Then, If you are using another user, procede.

- First of all you have to create the database. From Mysql console:
`CREATE DATABASE dxcluster;`

- Then   you have to give the right privileges to the user you are using for  dxspider.
For example:
`GRANT ALL PRIVILEGES ON dxcluster.* to 'sysop'@'localhost';`

- So  manually the spot table with the following command:


    CREATE TABLE 'spot' (
      'rowid' int(11) NOT NULL AUTO_INCREMENT,
      'freq' double NOT NULL,
      'spotcall' varchar(14) NOT NULL,
      'time' int(11) NOT NULL,
      'comment' varchar(255) DEFAULT NULL,
      'spotter' varchar(14) NOT NULL,
      'spotdxcc' smallint(6) DEFAULT NULL,
      'spotterdxcc' smallint(6) DEFAULT NULL,
      'origin' varchar(14) DEFAULT NULL,
      'spotitu' tinyint(4) DEFAULT NULL,
      'spotcq' tinyint(4) DEFAULT NULL,
      'spotteritu' tinyint(4) DEFAULT NULL,
      'spottercq' tinyint(4) DEFAULT NULL,
      'spotstate' char(2) DEFAULT NULL,
      'spotterstate' char(2) DEFAULT NULL,
      'ipaddr' varchar(40) DEFAULT NULL,
      PRIMARY KEY ('rowid'),
      KEY 'spot_ix1' ('time'),
      KEY 'spot_ix2' ('spotcall'),
      KEY 'spiderweb_spotter' ('spotter')
    ) ENGINE=InnoDB AUTO_INCREMENT=2598318 DEFAULT CHARSET=utf8mb4



- At the end, reboot your system.


