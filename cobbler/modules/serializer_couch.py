"""
Serializer code for cobbler.
Experimental:  couchdb version

Copyright 2006-2009, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
"""

import distutils.sysconfig
import os
import sys
import glob
import traceback
import yaml # PyYAML
import simplejson
import exceptions

plib = distutils.sysconfig.get_python_lib()
mod_path="%s/cobbler" % plib
sys.path.insert(0, mod_path)

from utils import _
import utils
from cexceptions import *
import os
import couch

typez = [ "distros", "profiles", "systems", "images", "repos" ]
couchdb = couch.CouchDb('127.0.0.1')

def register():
    """
    The mandatory cobbler module registration hook.
    """
    couchdb.connect()
    for x in typez:
        couch.createDb(x)
    return "serializer"

def serialize_item(obj, item):

    datastruct = item.to_datastruct()
    couch.saveDoc(obj.collection_type(),
                  simplejson.dumps(datastruct, encoding="utf-8"),
                  obj.name)
 
    return True

def serialize_delete(obj, item):
    couch.deleteDoc(obj.collection_type(),
                    item.name)
    return True

def deserialize_item_raw(collection_type, item_name):
    data = couch.openDoc(collection_type, item_name)
    return simplejson.loads(data, encoding="utf-8")

def serialize(obj):
    """
    Save an object to disk.  Object must "implement" Serializable.
    FIXME: Return False on access/permission errors.
    This should NOT be used by API if serialize_item is available.
    """
    ctype = obj.collection_type()
    if ctype == "settings":
        return True
    for x in obj:
        serialize_item(obj,x)
    return True

def deserialize_raw(collection_type):
    items = couch.listDoc(collection_type)
    if collection_type == "settings":
         fd = open("/etc/cobbler/settings")
         datastruct = yaml.load(fd.read())
         fd.close()
         return datastruct
    else:
         results = []
         for f in items:
             data = couch.openDoc(collection_type, f)
             datastruct = simplejson.loads(ydata, encoding='utf-8')
         return results    

def deserialize(obj,topological=True):
    """
    Populate an existing object with the contents of datastruct.
    Object must "implement" Serializable.  
    """
    datastruct = deserialize_raw(obj.collection_type())
    if topological and type(datastruct) == list:
       datastruct.sort(__depth_cmp)
    obj.from_datastruct(datastruct)
    return True

def __depth_cmp(item1, item2):
    d1 = item1.get("depth",1)
    d2 = item2.get("depth",1)
    return cmp(d1,d2)

if __name__ == "__main__":
    print deserialize_item_raw("distro","D1")

