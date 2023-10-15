#!/bin/bash
source /home/rein/oec_web/venv/bin/activate

echo "Pulling latest OEC"
pushd ../open_exoplanet_catalogue
git pull
popd

echo "Clean github host key"
ssh-keygen -R github.com
ssh-keyscan github.com >> ~/.ssh/known_hosts

echo "Working on exoplanet.eu"
python generate_exoplaneteu_systems.py download

echo "Working on ExoplanetArchive"
python generate_exoplanetarchive_systems.py download

echo "Working on Open Exoplanet Catalogue (only checking for new planets)"
python generate_openexoplanetcatalogue_systems.py

echo "Updating OEC"
pushd ../open_exoplanet_catalogue
cp systems/Sun.xml systems_exoplaneteu/
cp systems/Sun.xml systems_exoplanetarchive/
python cleanup.py systems_exoplaneteu
python cleanup.py systems_exoplanetarchive
git commit -a -m "Automated nightly update from oec_continuity"
git push
popd


echo "Updating OEC_gzip"
pushd ../oec_gzip
./update_everything.bash
popd

echo "Updating OEC_tables"
pushd ../oec_tables
./update_everything.bash
popd


echo "Updating OEC_iphone"
pushd ../oec_iphone/scripts
python create_data_iphone_11.python
popd
		
pushd ../oec_meta/
./update_everything.bash
popd

pushd ../oec_web/
touch oec.wsgi
popd
