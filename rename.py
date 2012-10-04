

import cloudfiles
import os.path
from helpers import short_hash
import sys

here = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(here, 'rackspace_creds.txt')
with open(path, 'r') as fh:
    creds = [x.strip() for x in fh.readlines() if x.strip()]

prefix = sys.argv[1]
print 'PREFIX: %s' % prefix
if prefix == 'count':
    count = 0
    prefix = None
else:
    count = -1

conn = cloudfiles.get_connection(*creds, servicenet=True)
container = conn.get_container('scrape_images')


last_name = None
last_last_name = 0
obj = 1
while obj:
    print 'last_name: %s' % last_name
    if last_name == last_last_name:
        break
    last_last_name = last_name
    for obj in container.get_objects(prefix=prefix, marker=last_name):
        try:
            last_name = obj.name
            if len(obj.name) > 11:

                if count != -1:
                    #print obj.name
                    if count % 1000 == 0:
                        print 'COUNT: %s' % count
                    count += 1
                    continue

                new_hash = short_hash(obj.read())
                print 'copying: %s => %s' % (obj.name, new_hash)
                obj.copy_to('scrape_images', new_hash)
                container.delete_object(obj.name)
                # make sure the new one exists
                #new_obj = container.get_object(new_hash)
                #assert new_obj.name == new_hash, '%s ; %s' % (new_obj.name, new_hash)
        except Exception, ex:
            print 'EXCEPTION: %s' % ex



print 'FINAL COUNT: %s' % count
