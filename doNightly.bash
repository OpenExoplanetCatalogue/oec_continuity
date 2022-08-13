#!/bin/bash
source venv/bin/activate

echo "Working on exoplanet.eu"
python generate_exoplaneteu_systems.py download
python findnew.py systems_exoplaneteu

echo "Working on ExoplanetArchive"
python generate_exoplanetarchive_systems.py download
#python findnew.py systems_exoplanetarchive

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
