SPIDERWEB
===

### Ham radio cluster web viewer for DxSpider

- **Author:** Corrado Gerbaldo - IU1BOW.
- **Mail:** <corrado.gerbaldo@gmail.com>
- **Licensing:** Gpl V3.0 see ["LICENSE"](LICENSE) file.
- **Languages:** This application is written in Python/flask,Javascript and HTML
___
**DXSpider** is a great DX Cluster software that has a usefull telnet interface. 
I wrote this application in order to add a web user interface to DXSpider and show the spots collected.
The user could see 50 spots at time and filter them by band, spotter continent and spotted continent.

For this application I've used:
- **Bootstrap** for stylesheet CSS
- **Jquery** In the header you can find the link to MS link
- **qrz.com** For each callsing found you can click on lens and you'll see him on qrz.com
- **www.countryflags.io** I used it for show the country flags
- **cookie-bar.eu** I use it for cookie bar

You can find my web site at [https://dxcluster.iu1bow.it](https://dxcluster.iu1bow.it)

### Changelog
see it on file ["CHANGELOG.md"](docs/CHANGELOG.md)

### Install            

**1) DXSpider**
First of all you have to installed [DXspider] (http://www.dxcluster.org/) and connected with some other cluster nodes.

**2) MariaDB / MySQL**
Then you have to install MariaDB on your web server, on the same server where DXSpider is running and configure DXSpider to use it: in your spider folder edit `local/DXVars.pm` adding these lines:
```DXWars.pm
# the SQL database DBI dsn
$dsn = "dbi:mysql:dxcluster:localhost:3306";
$dbuser = "your-user";
$dbpass = "your-password"; 
```
If you would change some MariaDB parameters, then you can find them in  `/etc/mysql/my.cnf` or `/etc/my.cnf`, depending on your distro.

**3) Python / Flask**
First of all you have to install the python3 pip installer
```console
foo@bar:~$ sudo apt install python3-pip
```

This application is based on Flask 
To install **Flask**:
```console
foo@bar:~$ pip3 install flask 
```
or
```console
foo@bar:~$ sudo -H pip3 install flask --system 
```
Then you have to install mysql libraries**:
```console
foo@bar:~$ pip3 install flask_mysqldb  
or
foo@bar:~$ sudo -H pip3 install flask_mysqldb --system 
```

Finally you have to install matplotlib in order to plots some graphics
```console
foo@bar:~$ pip3 install matplotlib 
or
foo@bar:~$ sudo -H pip3 install matplotlib --system   
```

**4) Configuration**
In the path `spiderweb/cfg/` rename `config.json.template` in `config.json`:
```console
foo@bar:~$ mv config.json.template config.json
```
then edit it and set the user and password of your database and the menu items.
Othewhise, if you preferr, you could use an utility for edit your configuration and menu. Go in "script" folder and run ./config.sh

```console
foo@bar:~$ cd scripts
foo@bar:~$ ./config.sh

*** DxSpider configuration ***
Configuration file loaded from: ../cfg/config.json

   h:  help
   vc: view config.
   ec: edit config.
   vm: view menu
   em: edit menu
   s:  save
   t:  load config. from template

   x:  exit

Make your choiche: 

```

In order to show the right *plots*, you have to generate them! 
To do so you have to run *.sh* files inside *scripts* folders, or the better way is to **schedule** them with your **crontab**
```console
foo@bar:~$ crontab -e
```
then edit it in a manner like this:
```crontab 
0 23 * * * /foo/bar/spiderweb/scripts/qso_months.sh > /dev/null 2>&1
*/15 * * * * /foo/bar/spiderweb/scripts/propagation_heatmaps.sh > /dev/null 2>&1
```

### Run test
Now you can run your web application with the following command:
```console
foo@bar:~$ python webapp.py
```
The flask default port is 5000, so you can see your web app, typing `http://localhost:5000` in your web browser.
Keep in mind that the flask web server, usually is used as a test server.

### Production
If your would run your application a production web server, install it on **Gunicorn** and **NGINX** (obviously you can choose your preferred proxy/web server instead). I'm also using **certbot** in order to manage SSL *Let's encrypt* certificates.

[At this link](https://noviello.it/come-installare-flask-con-gunicorn-e-nginx-su-ubuntu-18-10/) (in italian language) you can find a guide for install certbot, gunicorn and NGINX 
After installed it you can configure 

**Search engine indexing**
When you are on-line, if you would to index your website on search engines, you have to generate a file named sitemap.xml and put it in /static/ folder. There are many tool to generate sitemap.xml, for example https://www.xml-sitemaps.com/

**Index on MySQL
If you would to increase speed on callsign search, you could define some index on the table 'spot'. You can see more details on 'scripts/create_mysql_index.sql'
~  
### Screenshots
Screenshot
----------
<img src="docs/images/01_desktop_main.jpg" width="300"/>
<img src="docs/images/02_desktop_plot.jpg" width="300"/>
<p float="left">
<img src="docs/images/03_mobile_install.jpg" width="200"/>
<img src="docs/images/04_mobile_icon.jpg" width="200"/>
<img src="docs/images/05_mobile_splash.jpg" width="200"/>
<img src="docs/images/06_mobile_main.jpg" width="200"/>
</p>


### TODO
see it on file ["TODO.md"](docs/TODO.md)
