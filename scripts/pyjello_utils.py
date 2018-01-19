import os
import shutil
import logging
import datetime
import markdown
import pyjello_conf as pjc


def util_backup(filename):
    ts = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    newname = filename + '.' + ts + '.bkp'
    try:
        shutil.copy2(filename, newname)
        logging.info('File %s backed up as %s.' % (filename, newname))
    except Exception as e:
        logging.error('Failed to backup file %s due to %s' % (filename, str(e)))
        pass
    return True

def util_build_file_list(dirname, IGNORE_CREGEX):
    """
       Builds a list of dictionaries of the form -
          * { 'dir': ..., 'filename': ..., 'ctime': ..., 'mtime': ... }
    """
    outlist = []
    logging.info('Scanning directory: %s', dirname)
    try:
        with os.scandir(dirname) as filelist:
            filelist_filt = [a for a in filelist if a.is_file() and not any(list(map(lambda rg: True if rg.match(a.name) else False, IGNORE_CREGEX)))]
            outlist = [ {'dir': dirname, 'filename': a.name, 'ctime': a.stat().st_ctime, 'mtime': a.stat().st_mtime} for a in filelist_filt ]
            dirlist = [ a for a in filelist if a.is_dir() ]
            if len(dirlist) > 0:
                outlist.append(list(map(util_build_file_list, dirlist)))
    except FileNotFoundError:
        logging.error('Directory not found: %s' % dirname)
        pass
    except Exception as e:
        logging.error('Error due to %s' % e) 
    logging.debug('Filelist generated for %s as %s' % (dirname, outlist))
    return outlist

def util_sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
