import sqlite3
import logging
import pyjello_conf as pjc
import hashlib
import os
import re



class Checkpoint:
    """Compares file mtimes and hashes against database to identify files to rebuild"""
    
    def __init__(self, regex_comp_list):
        self.new_build = False
        self.conn = None
        self.fileinfo = []
        self.cre_ig = regex_comp_list
        self.process_file_list = []
        logging.info('Does pyjello.db exist?')
        if not os.path.isfile('pyjello.db'):
            logging.info('pyjello.db does not exist. New checkpointer build.')
            self.new_build = True
        else:
            logging.info('pyjello.db exists.')
        self.conn = sqlite3.connect('pyjello.db')
        if self.new_build:
            self.db_new_build()
        logging.debug('Checkpoint.__init__ complete.')


    def db_new_build(self):
        logging.info('New build for checkpointer. This is going to take some time.')
        # dir = content, content/tag content/category etc.
        # type = [static, dynamic]
        self.conn.execute('''CREATE TABLE checkpointer
                                    ( dir text, 
                                      type text, 
                                      filename text, 
                                      ctime text, 
                                      mtime text,
                                      postdate text,
                                      category text,
                                      tags text,
                                      other_attribs text, 
                                      hash text)''')
        self.populate_temp()
        self.conn.execute('''INSERT INTO checkpointer SELECT * FROM temp_status''')
        self.conn.commit()



    # BUG : ignore not filtering css~ files.    
    def _scan_dirs(self, dirlist, contenttype):
        logging.info('Scanning %s directories...' % contenttype)
        for dentry in dirlist:
            logging.info('... Scanning %s' % dentry)
            try:
                with os.scandir(dentry) as items:
                    for f in items:
                        #logging.debug(f)
                        if f.is_file() and not any(list(map(lambda rg: True if rg.match(f.name) else False, self.cre_ig))):
                            # TODO Support hash
                            self.fileinfo.append((dentry, contenttype, f.name, f.stat().st_ctime, f.stat().st_mtime, ''))
                        if f.is_dir():
                            self._scan_dirs([os.path.join(dentry, f.name)], contenttype)
            except FileNotFoundError:
                logging.error('%s directory %s not found!. Skipping.' % (contenttype, dentry))
                pass
            logging.info('... Finished scanning %s' % dentry)
        logging.info('Finished scanning %s directories.' % contenttype)
        return self.fileinfo

        
    def _populate_temp(self):
        logging.info('Scanning STATIC directories for changes.')
        self._scan_dirs(pjc.STATIC_DIRS, 'STATIC')
        logging.info('Scanning DYNAMIC directories for changes.')
        self._scan_dirs([a['content'] for a in pjc.CONTENT_MAPPING.values()], 'DYNAMIC')
        logging.debug('fileinfo variable generated.')
        logging.debug(self.fileinfo)
        logging.info('Rebuilding temp_status table.')
        try:
            self.conn.execute('''DROP TABLE temp_status''')
        except sqlite3.OperationalError as e:
            if e.args[0] == 'no such table':
                pass
        self.conn.execute('''CREATE TABLE temp_status AS SELECT * FROM checkpointer LIMIT 1''')
        self.conn.execute('''DELETE FROM temp_status''')
        logging.info('Inserting data into temp_status')
        if len(self.fileinfo) > 0:
            cur = self.conn.cursor()
            a = cur.executemany('''INSERT INTO temp_status
                                            VALUES (?, ?, ?, ?, ?, ?)''', self.fileinfo)
            cur.close()
        self.conn.commit()


        # INSIGHT : We're optimizing for small incremental deltas instead of deletes or major updates.
    def _generate_process_list(self):
        logging.info('Generating deltas to be processed.')
        cur = self.conn.cursor()
        cur.execute('''
                       SELECT dir, type, filename FROM 
                       (
                             SELECT a.dir, a.type, a.filename, a.ctime, a.mtime, a.hash, 
				    b.dir orig_dir, b.type orig_type, b.filename orig_filename, b.ctime orig_ctime, b.mtime orig_mtime, b.hash orig_hash
                               FROM temp_status a 
                    LEFT OUTER JOIN checkpointer b
                                 ON ( a.dir = b.dir
                                      AND a.type = b.type
                                      AND a.filename = b.filename
                                 )
                       )
                       WHERE mtime > orig_mtime
                       OR orig_filename is NULL
                   ''')
        self.process_file_list = [ {'dir': d, 'file': f, 'type': t} for (d,t,f) in cur.fetchall() ]
        logging.info('%d files to be processed.' % len(self.process_file_list))
        logging.debug('Files are -')
        for f in self.process_file_list:
            logging.debug(" -- %s", os.path.join(f['dir'], f['file']))
        return self.process_file_list

    
    def process_deltas(self):
        self._populate_temp()
        self._generate_process_list()



