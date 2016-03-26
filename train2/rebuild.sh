t1=$(date +"%s")
m sqlcreate -D |& grep -v Warning | sudo -u postgres psql
rm data/migrations/0001_initial.py
m makemigrations
m migrate
m build_stops
m parsexl ../../data-feb-2016/times/201501_short.xlsx
t2=$(date +"%s")
echo "Time took = $(($t2-$t1))"

