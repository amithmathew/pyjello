# Configuration variables for PyJello

OUTPUT_DIR = 'output'
STATIC_DIRS = ['static']
STATIC_INDEX = True
INDEX_FILE = 'static/index.html'
COMMON_TEMPLATES = 'templates/common'

BACKUP_ROOT = "backup"

PYJELLO_IGNORE = ['^#', '#$', '.*\~$', '\~$', '\.DS_Store'] # any regex to ignore while parsing directories.

CONTENT_MAPPING = {
    'blog' : { 'content' : 'content/blog',
               'output' : 'output/blog',
               'templates' : 'templates/blog'
    },
    'stories' : { 'content' : 'content/stories',
                   'output' : 'output/stories',
                   'templates' : 'templates/stories'
    }
}

DEFAULT_POSTDATE_FORMAT = "%B %d, %Y" # strftime format
DEFAULT_AUTHOR = ["Author's Name"]
DEFAULT_CATEGORY = ['Random']



MARKDOWN_EXTENSIONS = ['markdown.extensions.abbr',
                       'markdown.extensions.def_list',
                       'markdown.extensions.fenced_code',
                       'markdown.extensions.footnotes',
                       'markdown.extensions.tables',
                       'markdown.extensions.meta',
                       'markdown.extensions.nl2br',
                       'markdown.extensions.smarty',
                       'markdown.extensions.toc',
                       ]
