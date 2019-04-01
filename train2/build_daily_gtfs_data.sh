source /home/opentrain/.virtualenvs/train2/bin/activate
cd "$(dirname "${BASH_SOURCE[0]}")"
python manage.py build_daily_gtfs_data

