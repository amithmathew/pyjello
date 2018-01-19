import os
import shutil
import logging
import markdown
import pyjello_conf as pjc
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2 import exceptions as je
import pyjello_utils as pju
import datetime
from collections import OrderedDict

# Meta processing vars.


class MapProcessor:

    def __init__(self, mapping):
        self.processed = []
        self.md = None
        self.j2env = None
        self.mapping = mapping
        # Compile ignore regexes.
        self.RT_REGEX_COMP = list(map(re.compile, pjc.PYJELLO_IGNORE))
        logging.info('%d Ignore regexes compiled.' % len(self.RT_REGEX_COMP))
        logging.debug('MapProcessor.__init__ complete.')

# SECTION : Process Delta markdown and create files_meta_dict TODO
    def _build_meta_dict(self, metadict):
        """
        Given a dict of markdown meta attributes, does verification
        and fallback before building final dict.
        """
        
        indict = metadict
        outdict = OrderedDict()


        # Are there missing meta attribs that we should write
        # back into the file.
        rewrite_flag = False
        logging.debug('Rewrite_flag state is %s' % rewrite_flag)

        # Title
        if 'title' in metadict:
            outdict['title'] = metadict['title'][0]
            del indict['title']
        else:
            outdict['title'] = os.path.splitext(metadict['file'])[0]
            rewrite_flag = True
        
        # Date
        if 'postdate' in metadict:
            outdict['postdate'] = metadict['postdate'][0]
            del indict['postdate']
        else:
            outdict['postdate'] = datetime.datetime.today().strftime(pjc.DEFAULT_POSTDATE_FORMAT)
            rewrite_flag = True

    
        # Category
        if 'category' in metadict:
            outdict['category'] = metadict['category']
            del indict['category']
        else:
            outdict['category'] = pjc.DEFAULT_CATEGORY
            rewrite_flag = True

    
        # Author
        if 'author' in metadict:
            outdict['author'] = metadict['author']
            del indict['author']
        else:
            outdict['author'] = pjc.DEFAULT_AUTHOR
            rewrite_flag = True

        # Pinned?
        if 'pinned' in metadict:
            outdict['pinned'] = True
            del indict['pinned']
        else:
            outdict['pinned'] = False

        # Tags
        if 'tags' in metadict:
            outdict['tags'] = metadict['tags']
            del indict['tags']
        else:
            outdict['tags'] = None

        # Add any remaining custom attributes into outdict
        outdict.update(indict)

        outdict['rewrite'] = rewrite_flag

        return outdict


    def _process_content(self, mapname, filelist):
        """
         Pulls list of files to process from jello_delta.
         Converts markdown to html with jinja.
        """
        logging.info('Processing files for map %s' % mapname)
        logging.debug('File list extracted as %s' % filelist)

        indexlist = []

        if len(filelist) == 0:
            logging.info('No files to process for map %s!' % mapname)
            return []
        self.j2env = Environment(
            loader=FileSystemLoader(self.mapping[mapname]['templates']),
            autoescape=select_autoescape(['xml'])
        )

        # Load article.html
        template_name = 'article.html'
        logging.info('Processing %s' % template_name)
        try:
            article_temp = self.j2env.get_template(template_name)
            logging.debug('Loaded jinja2 template.')
        except je.TemplateNotFound:
            logging.error('Missing template %s!' % template_name)

        # List of files and attribs to be returned out.
        for entry in filelist:
            if not self.md:
                self.md = markdown.Markdown(output_format="xhtml5",
                                            extensions=pjc.MARKDOWN_EXTENSIONS)
                logging.debug('Initialized Markdown engine')

            logging.info("Processing content file : %s"
                         % os.path.join(entry['dir'], entry['filename']))

            f = open(
                os.path.join(entry['dir'],
                             entry['filename']),
                'r',
                encoding="utf-8"
            )
            read_text = f.read()
            f.close()
            # logging.debug("Text read as: \n %s" % read_text)
            md_converted = self.md.reset().convert(read_text)
            logging.debug('Metadata extracted by Markdown: %s' % self.md.Meta)
            md_meta = self._build_meta_dict(self.md.Meta)
            logging.debug('Metadata after pyjello processing: %s' % md_meta)
            if md_meta['rewrite']:
                logging.info('Adding meta attributes to file %s' % entry['filename'])
                # Backup vars
                tstamp = datetime.datetime.now().strftime("%Y%m%d%H24%M%S")
                bkp_path = os.path.join(pjc.BACKUP_ROOT,
                                self.mapping[mapname]['content'])
                os.makedirs(bkp_path, exist_ok=True)
                full_bkp_filepath = os.path.join(bkp_path, entry['filename'] + ".bkp." + tstamp)

                # Backup the existing md file
                shutil.copyfile(os.path.join(entry['dir'], entry['filename']), full_bkp_filepath)

                # Rewrite file.
                del md_meta['rewrite']
                outtext = []
                for k in md_meta.keys():
                    if isinstance(md_meta[k], bool) and md_meta[k]:
                        outtext.append(k + ": ")
                    elif isinstance(md_meta[k], list):
                        outtext.append(k + ": " + " ".join(md_meta[k]))
                    elif isinstance(md_meta[k], str):
                        outtext.append(k + ": " + md_meta[k])
                    else:
                        logging.info("Not writing attribute with key %s and value %s as it does not satisfy conditions." % (k, md_meta[k]))
                outtext.append("\n")
                outtext.extend(self.md.lines)
                f = open(
                    os.path.join(entry['dir'],
                                 entry['filename']),
                    'w',
                    encoding="utf-8"
                )
                f.write("\n".join(outtext))
                f.close()
                logging.info('Meta attributes added to file %s' % entry['filename'])

            logging.debug('Markdown converted for %s' % entry['filename'])
            logging.debug('Metadata extracted as %s' % md_meta)

            outfilename = os.path.splitext(entry['filename'])[0] + '.html'
            fulloutpath = os.path.join(self.mapping[mapname]['output'],
                                       outfilename)
            absfulloutpath = os.path.join(os.getcwd(), fulloutpath)
            logging.debug('Output will be written to %s' % absfulloutpath)
            os.makedirs(os.path.dirname(absfulloutpath), exist_ok=True)
            with open(absfulloutpath, 'w+') as o:
                o.write(article_temp.render(content=md_converted,
                                            meta=md_meta))
            logging.info('Output write complete for %s' % outfilename)
            md_meta['fullhtmlout'] = os.path.splitext(entry['filename'])[0] + '.html'
            indexlist.append(md_meta)
        logging.info('Content processing complete for map %s' % mapname)
        
        # Index Rebuild
        logging.info('Rebuilding index.html for mapname %s' % mapname)
        # Load article_list.html
        template_name = 'article_list.html'
        logging.info('Processing %s' % template_name)
        try:
            article_list_temp = self.j2env.get_template(template_name)
            logging.info('Loaded jinja2 template.')
        except je.TemplateNotFound:
            logging.error('Missing template %s!' % template_name)

        fulloutpath = os.path.join(self.mapping[mapname]['output'],
                                   'index.html')
        logging.info('Writing output to %s.' % fulloutpath)
        with open(fulloutpath, 'w+') as o:
            o.write(article_list_temp.render(content=indexlist))
        logging.debug('index.html written for map %s' % mapname)

# SECTION : PROCESS
    def process_map(self, mapname):
        """
        Run processing for a map.
        """
        logging.info('Processing for mapname %s STARTED.' % mapname)
        filelist = pju.util_build_file_list(self.mapping[mapname]['content'],
                                            self.RT_REGEX_COMP)
        self._process_content(mapname, filelist)
        logging.info('Processing for mapname %s complete.' % mapname)
