#!/bin/bash
source venv/bin/activate

echo "Working on exoplanet.eu"
#python generate_exoplaneteu_systems.py download

echo "Working on ExoplanetArchive"
#python generate_exoplanetarchive_systems.py download

echo "Updating OEC"
pushd ../open_exoplanet_catalogue
python cleanup.py systems_exoplaneteu
python cleanup.py systems_exoplanetarchive

popd
