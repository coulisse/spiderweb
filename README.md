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

### Change log
08/03/2020: beta release
___
02/06/2020: 1.0
- added cookie bar
- added cookie policy
- added nav bar
- added plots

___
16/06/2020: 1.1
- updated plots page in order to not cache images

___
20/06/2020: 1.1.1
- managed plot refresh

___
04/09/2020: 1.1.2
- Fix on continents.cfg
- minor changes on html tags

___
08/09/2020: 1.1.3
- pretty print html pages
- removed horizontal scrollbar 
- fixed icon apple not found

___
08/09/2020: 1.1.4
- Fixed menu on cookies and plots

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
This application is based on Flask (of course you have installed Python before...)
To install **Flask**:
```console
foo@bar:~$ pip install flask 
```
or
```console
foo@bar:~$ sudo -H pip install flask --system 
```
Then you have to install also **python-dev, ssl and mysql libraries**:
```console
foo@bar:~$ sudo apt-get install python-dev default-libmysqlclient-dev libssl-dev 
foo@bar:~$ sudo -H pip install flask_mysqldb --system 
```
Finally you have to install matplotlib in order to plots some graphics
```console
foo@bar:~$ sudo apt-get install python-matplotlib 
foo@bar:~$ sudo -H pip install --upgrade matplotlib   
```

**4) Configuration**
In the path `spiderweb/cfg/` rename `config.json.example` in `config.json`:
```console
foo@bar:~$ mv config.json.example config.json
```
then edit it and set the user and password of your database

In order to show the right plots, you have to generate them! 
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

~  

### TODO
- add comments to code
- add other plots
- manage common html parts with "includes"
- add callsign search
- improve the mobile experience

