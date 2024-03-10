### Change log
Date: 10/03/2024 
Release: v2.5.3
- adapted card size and text for mobile
- removed monitor
- removed cookie consent banner, since this application uses only technical cookies
- issue [#51] (https://github.com/coulisse/spiderweb/issues/51)   -- just for caching
- security [#22] (https://github.com/coulisse/spiderweb/security/dependabot/22)
  
___
Date: 03/12/2023 
Release: v2.5.2
- security issue #46.
- csp report
- Added esclusion for FT4 and FT8. Thanks to HB9VVQ
- Added filter on dx spot callsings. Thanks to HB9VVQ. Issue [#39](https://github.com/coulisse/spiderweb/issues/39).
- Sanitized callsign input
- Added propagation page with MUF Map. Issue [#27](https://github.com/coulisse/spiderweb/issues/27). Thanks to Paul Herman and Andrew Rodland 

___
Date: 12/11/2023 
Release: v2.4.5.1
- managed telnet password
- issue [#34](https://github.com/coulisse/spiderweb/issues/34)
- issue [#38](https://github.com/coulisse/spiderweb/issues/38)

___
Date: 11/11/2023 
Release: v2.4.5
- added "back to top" button
- enancement request #44  :  added reset filter
- fixed dependencie #32 : mysql connector
- fixed FT8 frequency on CW 6 meter band #40
- upgraded echarts library from 5.4.1 to 5.4.3
- upgraded flag icons library from 6.6.0 to 6.15
- upgraded bootstrap to 5.2.3

___
Date: 26/02/2023 
Release: v2.4.4
- replaced multipart form post with url encoded for security reasons
- fixed bands and continents in band activity chart
- upgraded Werkzeug to 2.2.3
- changed some api call from get to post method in order to not caching it
- fixed flags of Scothland and Northern Ireland

___
Date: 11/02/2023 
Release: v2.4.2
- changed cache-control header
- fixed Layout scrolling (SEO)
- first time spot load: not show cyan background
- efactor of the plot code
- fixed issue #31
- added PWA cache and improved service worker for offline

___
Date: 25/01/2023 
Release: v2.4.1.2
- fixed issue #30  bug on callsign search

___
Date: 23/01/2023 
Release: v2.4.1.1
- fixed issue #29  bug on callsign search

___
Date: 19/01/2023 
Release: v2.4.1
- changed dimensions of spots in world dx spost charts
- managed empty data in data providers for charts
- removed jQuery: migrated to vanilla javascript
- for spot refresh get only new spots starting from last rowid
- modified building script 
- moved cty file in data directory
- fixed issue #28
- cut comments too long
- charts layout changed
- reduced javascripts
- fixed issue #11 cookie consent request for non-https website

___
Date: 01/01/2023 
Release: v2.4
- migration to python 3.11
- added descriptions to continents
- fixed issue #23: Wrong flag for Cocos (Keeling) Islands
- proposal for improvements #25 (charts titles, removed link from connected nodes)
- reenginering of graph & stats
- upgraded bootstrap icons
- upgraded flag icons
- added new propagation chart https://sidc.be/silso/
- added Content Security Policy
___
Date: 28/09/2022 
Release: v2.3.4
- fixed issue #22 propagation_heatmaps.sh fails with 'Passing a Normalize instance simultaneously with vmin/vmax is not supported.' 
- replaced seaborn styles since are deprecated
___
Date: 23/08/2022                         
Release: v2.3.3
- modified minified system
- fixed qso_world_plot.py that hangs
___
Date: 23/08/2022                         
Release: v2.3.2
- upgraded Numpy library for security issues
- upgraded Mysql library for security issues
- upgraded to bootstrap 5.2
- upgraded flag-icon-css to 6.6.4
___
Date: 28/04/2022                         
Release: v2.3.1
- Fixed bug on adxo json that block entire website!
- upgraded Pillow library for security issues
___
Date: 04/03/2022                         
Release: v2.3
- lint on code with codefactor
- added new world qso in lasth month plot
___
Date: 13/01/2022                         
Release: v2.2
- fixed country code of Curacao
- managed CTY.dat file for a more precise localization of callsign
- bootstrap upgraded to 5.1.3
- added UTC clock in menu bar
- added cookie consent banner
- updated flag-icon-css
- modified modes.json in order to improve modes filter
- fixed forecast on  months plots
- upgraded pillow library to 9.0 for security issues
___
Date: 04/12/2021                         
Release: v2.1
- created a new "spider" icon
- jquery upgraded to 3.6
- bootstrap upgraded to 5.0.2
- managed connection error to telnet host 
- used a base template in order to put all csv/scripts on a page
- keywords changed
- added version to page footer
- created a build script in order to automating versioning and others
- added security policy in meta tag
- added cross-site request forgery security
- added security headers
- added cache control headers
___
16/05/2021: 2.0.2   
- Fixed frequency mode on 40 meters                                                    
- Fixed unicode query
- used qry.py also inside webapp.py
- replaced MySqlDb with mysql.connector
___
14/05/2021: 2.0.1   
- Addded installation with requirements                                                
___
06/05/2021: 2.0     
- Migrated to bootstrap 5                                                               
- Migrated to python 3
- Added configuration in config.json for telnet and mail address (so you can avoid to change index.html file)
- In the spot list, moved the country columns, after flag
- When press "search", collapse filters form
- Added mode filter
- fixed label on qso/months plot
- removed link to country-flags.io and used https://github.com/lipis/flag-icon-css hosted at https://cdnjs.com/libraries/flag-icon-css/3.4.1 in order to improve performances and remove cookies
- removed cookie bar
- improved offline page
- remove colors from callsing search resoults table
- added popover on mobile
- added monitor.sh in order to monitor your system
- added connected nodes in plots page (renamed as "plots and stats")
- added hour / band qso plot
- improved qso per month plot
- added plot trend
- improved logging
- insert bootstrap icons
- improved footer
- added "Announced Dx Operation" integration with ng3k website 
- used bootstrap icons instead of custom icons
- migrated to last jquery version 3.6.0
___
04/10/2020: 1.2.2
- Added config.sh utilty in script folder, in order to avoid edit manually config.json
- fixex menu on callsign page
___
21/09/2020: 1.2.1
- Added country column (only on desktop version)
- Added external configurable menu
- Renamed json.config.example json.config.template
- Added code of conduct and issue templates
___
08/09/2020: 1.2    
- Modified cookies.html in order to insert dinamically the host name (instead of dxcluster.iu1bobw.it)
- Removed sitemap.xml from git
- updated jquery version to 3.5.1
- added callsign search
- made flags responsive
- some little changes on meta tag and pages descriptions
- fixed day on datas 
___
08/09/2020: 1.1.4
- Fixed menu on cookies and plots
___
08/09/2020: 1.1.3
- pretty print html pages
- removed horizontal scrollbar 
- fixed icon apple not found
___
04/09/2020: 1.1.2
- Fix on continents.cfg
- minor changes on html tags
___
20/06/2020: 1.1.1
- managed plot refresh
___
16/06/2020: 1.1
- updated plots page in order to not cache images
___
02/06/2020: 1.0
- added cookie bar
- added cookie policy
- added nav bar
- added plots
___
08/03/2020: beta release
