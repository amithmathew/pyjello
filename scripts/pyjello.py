#!/usr/bin/env python3
import logging
import os
import sys
import pyjello_conf as pjc
import mapprocessor as mp
import distutils
from distutils import dir_util

## DEBUG, INFO, WARNING, ERROR, CRITICAL
### MapProcessorObject
###        Takes a contentmap
###        Builds list of md files
###        Initiates a DB Connection
###        Processes md files
###        Generates html
###        Generates index.html at root.
###        Loads delta data into sqlite db.
### 
# Find modified files.
## Checkpoint file
## Process each file
### Parameter parsing
### convert to html
### write to output folder.
### modify links
### Generate rss feeds.

def pjc_varcheck(conf_var, default_val):
     if hasattr(pjc, conf_var):
         logging.info('CONFIGURATION Variable found %s : %s', conf_var, vars(pjc)[conf_var])
     else:
         logging.info('CONFIGURATION Variable %s missing. Default set as %s', conf_var, default_val)
         setattr(pjc, conf_var, default_val)

def conf_checks():
         logging.info('Checking pyjello_conf, setting defaults.')
         # Variable checks.
         pjc_varcheck('OUTPUT_DIR', 'output')
         pjc_varcheck('STATIC_DIRS', "['static']")
         pjc_varcheck('STATIC_INDEX', 'True')
         pjc_varcheck('INDEX_FILE', 'static/index.html')
         pjc_varcheck('CHECK_DIFF_HASH', 'False')
         pjc_varcheck('PYJELLO_IGNORE', []) 

         for sd in pjc.STATIC_DIRS:
             if not os.path.isdir(sd):
                 logging.warning('Missing Static directory %s. Output may be missing.' % sd)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    logging.info('Starting PyJello')
    logging.debug(sys.argv[0])
    logging.debug('Setting working directory to %s' % os.path.join(os.path.dirname(sys.argv[0]),os.pardir))
    os.chdir(os.path.join(os.path.dirname(sys.argv[0]),os.pardir))
    conf_checks()

    # Static file processing.
    logging.info('Copying STATIC files to output directory : %s' % pjc.OUTPUT_DIR)
    for sd in pjc.STATIC_DIRS:
         logging.info('Copying files from directory : %s' % sd)
         distutils.dir_util.copy_tree(sd, pjc.OUTPUT_DIR, update=1)
    logging.info('STATIC file copy complete.')

    m = mp.MapProcessor(pjc.CONTENT_MAPPING)
    # Process content maps
    logging.info('Processing CONTENT maps for Dynamic Content')
    for cm in pjc.CONTENT_MAPPING.keys():
         logging.info('Processing map : %s' % cm)
         m.process_map(cm)
    logging.info('Jello set!')

if __name__ == '__main__':
    main()

    
