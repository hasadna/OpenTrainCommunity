import os
import tarfile
import tempfile
import shutil
import src.manage

TEMP_DATA_DIR_NAME = 'opentrain_data'
TAR_FILE = 'data/2013.tar.gz'

def extract_tar(tar_file, path):
  shutil.rmtree(path)
  os.mkdir(path)
  print "Extracting data files to {}".format(path)
  tar = tarfile.open(tar_file)
  tar.extractall(path=path)
  tar.close()

temp_dir = tempfile.gettempdir()
temp_data_dir = os.path.join(temp_dir, TEMP_DATA_DIR_NAME)
extract_tar(TAR_FILE, temp_data_dir)
src.manage.create_db()
for filename in os.listdir(temp_data_dir):
  full_filename = os.path.join(temp_data_dir, filename)
  src.manage.add_opentrain_data(full_filename)

