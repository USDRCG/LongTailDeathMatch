pushd ../..
bash reboot.sh
read -p "Press [Enter] when the screens come back up"
bash mountShare.sh
popd
