![PyJello - A Simple Static Site Generator](https://upload.wikimedia.org/wikipedia/commons/d/d0/Food-Jelly.svg)
# PyJello - A Simple Static Site Generator

## What is this?
PyJello was the fruit(haha!) of Python wielded in anger. I wanted a simple static site generator, that could handle static files without fuss, support Jinja2 and allow me to use MarkDown. I found Pelican unwieldy and too opiniated, and let's not even talk about Hugo. I decided that it made more sense to spend countless hours building my own framework than learning to use Pelican or Hugo, obviously.

## What makes PyJello so special, huh?
You mean other than the really cool name?

PyJello is extremely simple and configurable. 
* Great support for Static Files
* Build your templates in Jinja2
* Write your posts with Markdown.
* Meta-attribute support in Markdown.
* Supports any ordering in your index files - completely customizable.
* Supports multiple "article-lists" at multiple paths.

## Do you do any versioning or testing?
We are too cool for any of these.

I will be building out `unittest` cases soon.

No, seriously.

## Does this actually work? Where can we see it in action?
[My Personal Site - the raison d'etre for Pyjello](http://amithm.ca)

## Okay, we love it. Now how do I actually use the damn thing?
For now -
1. Download/Clone the repo.
2. Modify `scripts/pyjello_conf.py` to your liking.
3. Replace the existing `static/index.html` with your own.
4. Look at `templates/common/base.html`, `templates/blog/article.html` and `templates/blog/article_list.html`. Change according to taste.
5. Run `python scripts/pyjello.py`
6. Revel in the glory that is your new static site. (You'll find it in the output directory you defined in `scripts/pyjello_conf.py`.)

I'll be converting this into a module and publishing on pip soon.

## Can I contribute?
Yes. Pull requests are appreciated.

## Bugs
Too many at this point. But they will be squashed - maybe slowly, but mercilessly.

# Reference

## Special Markdown Attributes

title
: Title of the article/post

postdate
: Date of posting. PyJello will use `today()` as postdate if attribute is not specified.

draft
: Consider the post/article as Draft. Does not generate html. Only the attribute is required in your markdown file, you do not need to specifically set the attribute to `True`.

category
: Category. PyJello will use `DEFAULT_CATEGORY` from the configuration file if this attribute is not specified.

author
: Author. PyJello will use `DEFAULT_AUTHOR` from the configuration file if this attribute is not specified.

pinned
: Affects sort order by pinning the post to the top. Sort behaviour can be customized in the article_list template, and you can choose to ignore this attribute. PyJello will set this to `false` if this attribute is not specified. Only the attribute is required in your markdown file, you do not need to specifically set the attribute to `True`.

tags
: Tags. Optional attribute, and will be ignored if not specified. 