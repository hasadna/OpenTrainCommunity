import os
import tarfile
import tempfile
import shutil
import src.manage
import time
import datetime

TEMP_DATA_DIR_NAME = 'opentrain_data'
TAR_FILE_2013 = 'data/2013.tar.gz'
TAR_FILE_2014 = 'data/2014-01Jan-to-10Aug.tar.gz'

def extract_tar(tar_file, path):
  if os.path.isdir(path):
    shutil.rmtree(path)
  os.mkdir(path)
  print "Extracting data files to {}".format(path)
  tar = tarfile.open(tar_file)
  tar.extractall(path=path)
  tar.close()

def fix_2014_file(full_filename, fixed_full_filename):
  cmd = "cat " + full_filename + " | cut -c 2-39 | sed -r -e 's/^.{8}/& /' | awk -v OFS=\"\t\" '$1=$1' > " + fixed_full_filename
  os.system(cmd)

start = time.time()

temp_dir = tempfile.gettempdir()
temp_data_dir = os.path.join(temp_dir, TEMP_DATA_DIR_NAME)
src.manage.create_db()
# load 2013 data:
if True:
  extract_tar(TAR_FILE_2013, temp_data_dir)
  for filename in os.listdir(temp_data_dir):
    if os.path.basename(filename) != "2013-12.txt":  # "2013-12.txt" is identical to "12_2013.txt"
      full_filename = os.path.join(temp_data_dir, filename)
      src.manage.add_opentrain_data(full_filename)

# load 2014 data:
if True:
  extract_tar(TAR_FILE_2014, temp_data_dir)
  filename = os.listdir(temp_data_dir)[0]  # there is just one file
  full_filename = os.path.join(temp_data_dir, filename)
  fixed_full_filename = os.path.join(temp_data_dir, '2014_fixed.txt')
  fix_2014_file(full_filename, fixed_full_filename)
  src.manage.add_opentrain_data(fixed_full_filename)

shutil.rmtree(temp_data_dir)

elapsed = (time.time() - start)
print "setup_db done. Elapsed time:", str(datetime.timedelta(seconds=round(elapsed)))