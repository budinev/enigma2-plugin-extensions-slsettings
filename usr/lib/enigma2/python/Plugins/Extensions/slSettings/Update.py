import os, re, sys
from twisted.web.client import downloadPage
PY3 = sys.version_info.major >= 3
print("Update.py")
def upd_done():        
    print( "In upd_done")
    xfile ='http://sat-lodge.it/slsettings.tar'
    print('xfile: ', xfile)
    if PY3:
        xfile = b"http://sat-lodge.it/slsettings.tar"
    print("Update.py not in PY3")
    fdest = "/tmp/slsettings.tar"
    print("upd_done xfile =", xfile)
    downloadPage(xfile, fdest).addCallback(upd_last)

def upd_last(fplug): 
    cmd = "tar -xvf /tmp/slsettings.tar -C /"
    print( "cmd A =", cmd)
    os.system(cmd)
    pass

