#!/usr/bin/env python

from cmislib.model import CmisClient, CmisException
import os, traceback, time

from config import *

def compare(fd1, fd2):
    """Compares two open files given by file descriptors fd1 and fd2.

    Actually only compares the firts 1M bytes, because I'm lazy."""

    s1 = fd1.read(1000000)
    s2 = fd2.read(1000000)
    return s1 == s2

def main():
    """Main method (split it if you want cleaner code.

    Creates a folder called "TEST", then stuffs if with the content of the local
    folder specified in config.py.
    """

    client = CmisClient(REPOSITORY_URL, USERNAME, PASSWORD)
    repo = client.getDefaultRepository()
    root_folder = repo.getObjectByPath(REMOTE_PATH)

    # Removes the TEST folder if it already exists
    try:
        object = repo.getObjectByPath(REMOTE_PATH + "/TEST")
        object.deleteTree()
    except:
        pass

    root_folder.createFolder("TEST")

    start_time = time.time()

    for root, dirs, files in os.walk(LOCAL_PATH):
        root_rel = root[len(LOCAL_PATH):]
        remote_parent = repo.getObjectByPath(REMOTE_PATH + "/TEST" + root_rel)
        for dir in dirs:
            # FIXME later: skip non-ascii file names
            if dir.encode("ascii", errors="replace") != dir:
                continue

            print "----"
            print ("creating dir: %s" % dir).encode("ascii", errors="replace")
            remote_parent.createFolder(dir)

        for file in files:
            # FIXME later: skip non-ascii file names
            if file.encode("ascii", errors="replace") != file:
                continue

            print "----"
            if os.stat(os.path.join(root, file)).st_size > 1e6:
                print ("File %s too big, skipping" % file).encode("ascii", errors="replace")
                continue

            print ("Creating file: %s" % file).encode("ascii", errors="replace"),
            try:
                local_fd = open(os.path.join(root, file))
                created = remote_parent.createDocument(file, contentFile=local_fd)
                local_fd.close()
                print "OK"
            except AssertionError, e:
                print "KO: exception raised"
                print e
            except CmisException, e:
                print "KO: exception raised"
                print e
            print "nNote: remote name is:", created.properties["cmis:name"].encode("ascii", errors="replace")

            print ("Verifying file: %s" % file).encode("ascii", errors="replace"),
            try:
                path = REMOTE_PATH + "/TEST" + root_rel + "/" + file
                object = repo.getObjectByPath(path)
                remote_fd = object.getContentStream()
                local_fd = open(os.path.join(root, file))
                if compare(local_fd, remote_fd):
                    print "OK"
                else:
                    print "KO: Content differs"
            except AssertionError, e:
                print "KO: exception raised"
                print e
            except CmisException, e:
                print "KO: exception raised"
                print e

    end_time = time.time()
    print "Elapsed time:", end_time - start_time



main()