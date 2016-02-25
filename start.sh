#
# This script starts first back end and then front end
#

echo "Starting back end"
sudo python new_format.py

Sleep 1

echo "Starting front end"
sudo python piShark/main.py
