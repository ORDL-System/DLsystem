ports=(5001 8500 8501 8502 8503 8504 8602 8702 8801 8802 8803 8901 9001 9002)
for port in "${ports[@]}"
do
kill $(lsof -i:$port | awk '{print $2}' | awk 'NR==2{print}')
done