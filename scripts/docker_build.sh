cd ..
version=$(cat static/version.txt)
docker build -t spiderweb:${version} .
cd scripts
