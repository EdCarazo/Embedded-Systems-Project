#
# This script starts first back end and then front end
#
echo "Starting back end"
sudo python new_format.py

echo "Starting front end"
sudo python piShark/main.py
