# restarts pi01-pi09
for i in {1..9}
do
	ssh pi0$i 'sudo shutdown -r 0'
done
