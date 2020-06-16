#used to minify the application javascript                            
curl -X POST -s --data-urlencode 'input@application.js' https://javascript-minifier.com/raw > application.min.js
curl -X POST -s --data-urlencode 'input@application_inline.js' https://javascript-minifier.com/raw > application_inline.min.js
curl -X POST -s --data-urlencode 'input@load-sw.js' https://javascript-minifier.com/raw > load-sw.min.js
curl -X POST -s --data-urlencode 'input@plot_inline.js' https://javascript-minifier.com/raw > plot_inline.min.js
