#! /usr/bin/env python

# Copyright (c) 2025 Grayson Bray Morris.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# litesite: a simple static site generator written in Python.
# -------------------------------------------------------------
# https://github.com/gbmj/litesite
# -------------------------------------------------------------
# This file is a well-documented version of the script, meant to
# be self-contained and provide command line help. Feel free
# to delete any "help" you don't need, including type hinting
# and inline comments. Above all, fee free to remove the 200 lines
# of docstring below -- it's reproduced in the README at GitHub.

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "python-frontmatter" = ">=1.1",
#     "pandoc" = ">=3.8",
#     "pypandoc" = ">=1.15",
# ]
# ///

"""Generate a static site for a blog-like collection of pages.

litesite gives you nearly total freedom to design your site. The
script simply stitches together repeated content, such as headers,
sidebars and footers, with page-specific content. How you structure
those elements is up to you. The purpose is to reduce the work of
tweaking something that repeats across many pages: using litesite,
you change it once, and it propagates to all relevant pages on your
next build.

Examples: visit https://github.com/gbmj/gbmj-net

How to Use:
    Copy litesite.py into the root folder of the site you want to
    build and edit the USER SETTINGS section. Create your common and
    page-specific input files (see `Assumed folder structure`),
    using content placeholders where desired (see `Placeholders`). Feel
    free to add custom logic to process your own tags and placeholders;
    the script indicates where such logic is needed.

    Use your preferred package manager to install the script's external
    dependencies (see `Requirements`), update the shebang line as needed,
    and run.

Requirements:
    - python 3.13 or later
    - pypandoc 1.15 or later (plus pandoc 3.8 or later),
      see pypi.org/project/pypandoc/
    - python-frontmatter 1.1 or later, see pypi.org/project/python-frontmatter/
    - the common head, pre and post files must contain valid html; the
      script will insert them as is. The common head file must begin
      and end with <head> resp </head>.
    - you can use any file extension you like for your input files,
      including one you made up, but the actual content must be in
      a pandoc-supported input format. See pandoc.org/MANUAL.html#options.
    - all input files you want the script to process must include a
      YAML frontmatter block containing `litesite:`. Files without this
      tag will be ignored.

Assumed file & folder structure:
    litesite.py         (this file; required)
    *.foo               (0+ input files; ext customizable)
    *.*                 (0+ other files/folders)
    cmn/                (required; name customizable)
       |_ head.html     (required; name customizable)
       |_ cpre.html  (required; name customizable)
       |_ cpost.html  (required; name customizable)
       |_ npre.html  (optional; name customizable)
       |_ npost.html  (optional; name customizable)
    */                  (0+ other folders)
        |_ *.foo        (0+ input files)
        |_ *.*          (0+ other files)
        |_ */           (0+ subfolders with similar structure)

The script generates an html page for each input file in the root
folder plus subfolders up to MAXDEPTH (customizable). Each html
page uses the name of its input file. Example:
coolest-page-ever.foo will generate coolest-page-ever.html.

The script distinguishes between standalone pages and pages that
are part of a Collection. You tell the script which is which
using YAML frontmatter:
    - input files tagged `litesite: collection` generate Collection pages.
    - input files tagged `litesite:` with any other value (including
      an empty string) generate standalone pages.
    - input files with no `litesite:` tag do not generate html pages.
      This means you can also use the chosen extension for other things.

Collection pages use the cpre and cpost files; standalone pages
use npre and npost. This allows you to tailor the common elements
to the page type. If you want all pages to have the same common parts,
set the same filenames for both in USER SETTINGS.

The home page is a special case. If there is no top-level index.foo,
the script will create the page from scratch, using cpre and cpost
and adding a table of contents (TOC) listing the Collection. If
index.foo does exist, the script will build a regular standalone page,
then scan the result for a TOC placeholder (see `Placeholders`). If found,
the script inserts a TOC at this location.

Styling the TOC:
    The generated table of contents includes a title, optional subtitle,
    optional year headings, and a list of links to pages in the Collection,
    with or without descriptive blurbs. Because the TOC is
    generated and not under your direct control, the script provides
    three customizable css classes so you can fine-tune its styling.
    See USER SETTINGS in the script.

Optional frontmatter:
    In addition to the required `litesite:`, the script recognizes
    three optional frontmatter tags:
        title: Title of Page
        date: YYYY-MM-DD
        blurb: A short summary to use in the table of contents.

    The date can be any valid ISO 8601 timestamp with at least the
    fields shown above. You don't need to wrap the title or blurb in
    quote marks, but you may. The tags can be in any order and additional
    frontmatter is fine; the script will ignore it (unless you add logic
    to handle it; see `Custom tags and placeholders`.)

    For missing tags, the script defaults to:
        title: Titlecased Name Of File With Dashes Converted To Spaces
        date: 0001-01-01
        blurb: ''

    (For files named `index`, the script defaults to the name of the
    enclosing folder.)

Placeholders:
    The script offers several out-of-the-box placeholders you can
    use in your head, pre, post and *.foo files. You can also create
    your own. The naming convention is meant to help you
    produce valid html:
        *_TEXT_PH - use anywhere ordinary text is valid
        *_URL_PH - of the form https://bar.foo/baz; use anywhere
                   a full web address including protocol is valid
        *_LINK_PH - of the form
                    <a href="https://bar.foo/baz">previous</a>;
                    use anywhere a complete anchor element is valid

List of standard placeholders:
    In the list below, (scope) indicates the pages on which the
    script will process the given placeholder. If you use a
    placeholder outside its scope, it will still be there in the
    final page (unless you modify the script to handle it).

(any)   DOMAIN_URL_PH, HOME_URL_PH - a convenience for converting
            relative links to absolute. Use these when you link to
            other pages on your domain, and you will only
            have to update two constants in this script if you change
            domain names or move the site folder. Note, these URLs
            contain a trailing slash, so proper use will look funny:
            For example, write <img href="DOMAIN_URL_PHimages/me.png" />
            and not <img href="DOMAIN_URL_PH/images/me.png" />.
(any)   NAME_DOMAIN_TEXT_PH, SITENAME_TEXT_PH - insert the name
            of the overarching domain resp. this site. Useful for
            subsites that point back to the main site.
(any)   SELF_URL_PH - insert the absolute URL to the current page.
            Exclusively for a rel="canonical" link in your head file.
            The script disables all other self-links on a page.
(any)   YEAR_TEXT_PH, DATE_TEXT_PH - insert the year resp. full date
            specified in the page's frontmatter (else the default value).
            Note, the date will be in ISO 8601 format. Modify this
            script if you want something prettier :).
(any)   TITLE_TEXT_PH - insert the title specified in the page's
            frontmatter (else the default value). Use in the head file's
            <title></title> element (and elsewhere as you desire).
(coll)  PREV_URL_PH, NEXT_URL_PH - insert URLs to the page's TOC
            neighbors. Note, for nav links in headers, sidebars etc.
            you might prefer the _LINK_ versions below.
(coll,  PREV_LINK_PH, HOME_LINK_PH, NEXT_LINK_PH - insert the entire
home        anchor element for the page's TOC neighbors resp. the home
w/no        page. Use these instead of the _URL_ placeholders to 'gray
.foo        out' nav links that shouldn't be active: the TOC link on the
file)       home page itself, and the previous resp. next links on
            the first resp. last pages in the Collection.
(home   TOC_BLOCK_PH - insert a table of contents listing the Collection,
with        with links to each page. Only active on the site's home
.foo        page, and only if there's a corresponding index.foo file.
file)

Custom tags and placeholders:
    You can process custom frontmatter tags and/or placeholders by
    adding the required logic where indicated in the script comments.

Tips:
    The script starts from the directory you run it in and creates a
    self-contained site -- so you could run separate copies in several
    folders on your domain, creating multiple self-contained collections
    with their own styling and navigation. If you do that, be sure to
    set MAXDEPTH so you don't overwrite files in subfolders where you're
    running the script independently. If you need to process files in
    some subfolders but want others to run independently, use different
    file extensions for each site. See an example of the latter at
    https://github.com/gbmj/gbmj-net.

    You can create a non-blog-like site simply by omitting
    blog-like navigation placeholders (those with PREV, NEXT, TOC) and
    using the same pre and post files for all pages, or by having
    no input files with `litesite: collection` in the frontmatter.

    If you write your content in markdown: pandoc supports a whole
    lot of fancy stuff out of the box (fenced code, header attributes,
    definition lists, pipe tables, ...) without extra options or
    extensions, if you use 'markdown' as your input format. See
    https://pandoc.org/MANUAL.html#pandocs-markdown.

Limitations:
    This script is only aware of page-level common elements:
    their contents are inserted between the <body> and <main> (
    resp. </main> and </body>) tags. If you need section-level headers,
    footers, nav blocks or other in-page content that repeats on all pages,
    check out a more full-featured site generator like Jekyll or
    Hugo. Or edit this script. Or write your own! It's fun :).

    The script puts the same language tag on every html page; if you
    write content in two or more languages, you could use different
    infile extensions for them and run a different copy of the script
    for each; or you could modify the script to process more langs.

    I've mostly kept this script from enforcing particular
    choices, except for two:
        - the URL it generates for pages named `index` goes to the
          enclosing folder and contains a trailing slash.
        - the generated TOC is hardcoded to use h1 for its title,
          p for its subtitle, and ul for its contents.
    Modify the script if you prefer different behavior.
"""

import datetime as dt
from operator import itemgetter
from pathlib import Path
import re
import typing as typ  # type hinting support; remove if you remove type hints
import frontmatter  # parse input files containing YAML frontmatter
import pypandoc as ppd  # convert input files to html

#   -- USER SETTINGS ---
SITE_NAME = "Bob's Fabulous World of Dogs"  # name of this site
LANGUAGE = 'en'  # two-letter iso code
DOMAIN_SITENAME = 'Robert E. Doggson'  # if this is a subsite of your main site
DOMAIN = 'https://robedogg.xyz/'  # include protocol and end in /
PATH_FROM_DOMAIN_TO_HERE = 'all-the-dogs/'  # end in / if not ''
HHF_SUBDIR = 'cmn/'  # where head, pre, post files are; end in /
HDFN = 'head.html'
PREFN_C = 'cpre.html'
PREFN_NC = 'npre.html'
POSTFN_C = 'cpost.html'
POSTFN_NC = 'npost.html'
INFILE_EXT = 'dogpage'  # can be anything; no leading dot
CONVERT_FROM = 'markdown'  # pandoc input type, with optional extensions
OPTS: list[str] = []  # pandoc options to pass in during conversion
MAXDEPTH = 3  # 1 = root only
SORTKEY = 1  # 0 = title, 1 = date, anything else = don't sort
SORT_REVERSED = True
TOC_TITLE = "All Bob's Canine Friends"
TOC_SUBTITLE = ''  # can be empty
TOC_PRINT_YEAR_HEADINGS = False
TOC_PRINT_BLURBS = True
TOC_CLASS_NAME = 'toc'  # for css styling
TOC_NOBLURB_CLASS = 'noblurb'  # css class added on if PRINT_BLURBS = False
TOC_HAS_SUBTITLE_CLASS = 'has-subtitle'  # added if TOC_SUBTITLE not empty
TOC_JUMPTO_ID = ''  # '' or '#foo' for any foo; note leading #
PREV_ANCHOR_TXT = 'prev'
HOME_ANCHOR_TXT = 'TOC'
NEXT_ANCHOR_TXT = 'next'
# ---- END USER SETTTINGS ----

BASEURL = DOMAIN + PATH_FROM_DOMAIN_TO_HERE  # web address to folder
BASEDIR = Path(__file__).parent  # local filepath to folder
HEAD_PATH = BASEDIR / HHF_SUBDIR / HDFN
PRE_PATH_C = BASEDIR / HHF_SUBDIR / PREFN_C
POST_PATH_C = BASEDIR / HHF_SUBDIR / POSTFN_C
PRE_PATH_NC = BASEDIR / HHF_SUBDIR / PREFN_NC
POST_PATH_NC = BASEDIR / HHF_SUBDIR / POSTFN_NC
PPD_HTML_TYPES = ['html', 'html4', 'html5']


def _create_html_template(
    headfile: Path, prefile: Path, postfile: Path
) -> str:
    """Return a valid html page with a placeholder for later content."""
    head = headfile.read_text()
    pre = prefile.read_text()
    post = postfile.read_text()

    html = '<!DOCTYPE html>\n'
    html += '<html lang="' + LANGUAGE + '">\n'
    html += head
    html += '\n\n<body>\n\n'
    html += pre
    html += '\n<main>\n'
    html += '<!--BODY-->'
    html += '</main>\n\n'
    html += post
    html += '\n\n</body>\n\n'
    html += '</html>'

    return html


def _get_infiles(
    dir: Path, pattern: str, maxdepth: int = 10
) -> typ.Generator[typ.Iterator[Path]]:
    """Return a list of paths to files that contain `pattern`."""
    files = dir.glob(pattern)
    dirs = [c for c in dir.iterdir() if c.is_dir()]
    yield files
    if maxdepth > 1:
        for path in dirs:
            for x in _get_infiles(path, pattern, maxdepth - 1):
                yield x


def _create_meta_defaults(path: Path) -> dict[str, typ.Any]:
    """Set up fallback values for page metadata."""
    m: dict[str, typ.Any] = {}

    p = path.parent if path.stem == 'index' else path

    m['title'] = p.stem.replace('-', ' ').title()
    m['date'] = dt.date(1, 1, 1)  # January 1, 0001
    m['blurb'] = ''
    u = f'{BASEURL}{str(p.relative_to(BASEDIR))}'
    u = u + '/' if path.stem == 'index' else u.replace(f'{INFILE_EXT}', 'html')
    # pathlib relative_to returns . if paths are the same;
    # strip off the trailing ./ in that case
    m['url'] = u if not p.samefile(BASEDIR) else u[:-2]
    m['path'] = path.with_suffix('.html')

    # --- CUSTOM ---
    # add your custom defaults here, for example:
    #    m['breed'] = 'mutt'
    #    m['age'] = 0
    #    m['name'] = ''
    # --- END CUSTOM ---

    return m


def _process_incoming_meta(
    current: dict[str, typ.Any], new: dict[str, typ.Any]
) -> None:
    """Replace current values with new ones if present, ignoring keys not
    already in current."""
    # don't assume the values in `new` are of the type you expect --
    # for example, frontmatter.parse returns a boolean, not the
    # actual value, for strings/ints like `yes`, `no`, `0`, ``, ...
    for key, val in new.items():
        if val and (key in current):
            current.update({key: val})


def _process_complex_meta(meta: dict[str, typ.Any]) -> None:
    """Do any further processing on page metadata."""
    # baked-in metadata doesn't need further processing,
    # unless you change that

    # --- CUSTOM ---
    # process custom metadata here. For example:
    # if meta['breed']:
    #     meta['breed'] = f'Member of the <em>{meta["breed"]}</em> breed.'
    # if meta['age']:
    #    if meta['name']:
    #         meta['age'] = f'{meta["name"]} is {meta["age"]} years old.'
    #     else:
    #         meta['age'] = f'Age: {meta["age"]}'
    pass
    # --- END CUSTOM ---


# --- testing ---
_testing = False

if _testing:
    # test something here
    print('testing...')
# --- end testing ---

if __name__ == '__main__' and not _testing:
    coll: list[tuple[str, dt.date, str, str, Path]] = []
    idx_title, idx_date, idx_blurb, idx_url, idx_path = 0, 1, 2, 3, 4

    template_c = _create_html_template(HEAD_PATH, PRE_PATH_C, POST_PATH_C)
    template_nc = _create_html_template(HEAD_PATH, PRE_PATH_NC, POST_PATH_NC)

    for files in _get_infiles(BASEDIR, rf'*.{INFILE_EXT}', MAXDEPTH):
        for filepath in files:
            tags, body = frontmatter.parse(filepath.read_text())
            if 'litesite' in tags:
                html_body = (
                    ppd.convert_text(
                        body, 'html', CONVERT_FROM, extra_args=OPTS
                    )
                    if CONVERT_FROM not in PPD_HTML_TYPES
                    else body
                )
                m = _create_meta_defaults(filepath)
                _process_incoming_meta(m, tags)
                _process_complex_meta(m)
                if tags['litesite'] == 'collection':
                    coll.append(
                        (
                            m['title'],
                            m['date'],
                            m['blurb'],
                            m['url'],
                            m['path'],
                        )
                    )
                    html_page = template_c.replace('<!--BODY-->', html_body)
                else:
                    html_page = template_nc.replace('<!--BODY-->', html_body)

                # replace most placeholders now -- only SELF_URL_PH has to wait
                html_page = (
                    html_page.replace('TITLE_TEXT_PH', m['title'])
                    .replace('NAME_DOMAIN_TEXT_PH', DOMAIN_SITENAME)
                    .replace('SITENAME_TEXT_PH', SITE_NAME)
                    .replace('HOME_URL_PH', BASEURL)
                    .replace('DOMAIN_URL_PH', DOMAIN)
                    .replace('YEAR_TEXT_PH', str(m['date'].year))
                    .replace('DATE_TEXT_PH', str(m['date']))
                )

                # a page shouldn't have a link to itself, other than
                # the canonical in the head section, which we haven't yet
                # filled in. That means we can replace any self-links
                # we do find with just the link text
                if m['url'] in html_page:
                    html_page = re.sub(
                        rf'<a href="{m["url"]}">(.*?)</a>', r'\1', html_page
                    )

                # now we can fill in the canonical ref in head
                html_page = html_page.replace('SELF_URL_PH', m['url'])

                # --- CUSTOM ---
                # process any custom placeholders here, for example:
                # html_page = (
                #     html_page.replace('DOG_BREED', m['breed'])
                #     .replace('DOG_NAME', m['name'])
                #     .replace('DOG_AGE', str(m['age']))
                # )
                # --- END CUSTOM ---

                m['path'].write_text(html_page)

    # all infiles have been processed; now sort the Collection and
    # create the TOC in pandoc markdown

    if SORTKEY in [0, 1] and coll:
        key = itemgetter(SORTKEY)
        rev = SORT_REVERSED
        sorted_meta = sorted(coll, key=key, reverse=rev)
    else:
        sorted_meta = coll

    toc_md = f'# {TOC_TITLE}\n\n'
    toc_md += f'{TOC_SUBTITLE}\n\n' if TOC_SUBTITLE else ''
    year = 2  # the year 0002 -- must not equal date meta default

    for idx, (title, date, blurb, url, path) in enumerate(sorted_meta):
        # add page listing to TOC
        if TOC_PRINT_YEAR_HEADINGS and (date.year != year):
            toc_md += f'\n{date.year}\n\n'
            year = date.year
        toc_md += f'- [{title}]({url})'
        toc_md += f' &mdash; {blurb}\n' if TOC_PRINT_BLURBS else ''
        toc_md += '\n'

        # update nav links in page itself
        prev = PREV_ANCHOR_TXT
        if idx != 0:
            prev = f'<a href="{sorted_meta[idx - 1][idx_url]}">{prev}</a>'
        home = f'<a href="{BASEURL}{TOC_JUMPTO_ID}">{HOME_ANCHOR_TXT}</a>'
        next = NEXT_ANCHOR_TXT
        if idx != len(sorted_meta) - 1:
            next = f'<a href="{sorted_meta[idx + 1][idx_url]}">{next}</a>'
        html_page = path.read_text()
        html_page = (
            html_page.replace('PREV_LINK_PH', f'{prev}')
            .replace('HOME_LINK_PH', f'{home}')
            .replace('NEXT_LINK_PH', f'{next}')
        )
        path.write_text(html_page)

    # complete the TOC
    toc_classes = TOC_CLASS_NAME
    toc_classes += f' {TOC_NOBLURB_CLASS}' if not TOC_PRINT_BLURBS else ''
    toc_classes += f' {TOC_HAS_SUBTITLE_CLASS}' if TOC_SUBTITLE else ''
    toc = f'<section class="{toc_classes}" id="{TOC_JUMPTO_ID}">\n'
    toc += ppd.convert_text(toc_md, 'html', 'markdown+smart')
    toc += '</section>'

    # update / create the home page
    outfile = BASEDIR / 'index.html'
    infile = BASEDIR / f'index.{INFILE_EXT}'
    if infile.exists():
        # update the existing index.html
        html_page = outfile.read_text().replace(
            '<p>TOC_BLOCK_PH</p>', (toc if sorted_meta else '')
        )
    else:
        # create index.html from scratch
        prev = PREV_ANCHOR_TXT
        next = NEXT_ANCHOR_TXT
        if sorted_meta:
            prev = f'<a href="{sorted_meta[-1][idx_url]}">{prev}</a>'
            next = f'<a href="{sorted_meta[0][idx_url]}">{next}</a>'
        html_page = (
            template_c.replace('TITLE_TEXT_PH', TOC_TITLE)
            .replace('NAME_DOMAIN_TEXT_PH', DOMAIN_SITENAME)
            .replace('SITENAME_TEXT_PH', SITE_NAME)
            .replace('SELF_URL_PH', BASEURL)
            .replace('HOME_URL_PH', BASEURL)
            .replace('DOMAIN_URL_PH', DOMAIN)
            .replace('PREV_LINK_PH', prev)
            .replace('HOME_LINK_PH', HOME_ANCHOR_TXT)
            .replace('NEXT_LINK_PH', next)
            .replace('YEAR_TEXT_PH', '')
            .replace('DATE_TEXT_PH', '')
        )
        # --- CUSTOM ---
        # if you added custom placeholders that appear
        # in the pre and/or post for Collection pages,
        # set them appropriately for this page. For example:
        # html_page = (
        #     html_page.replace('DOG_BREED', '')
        #     .replace('DOG_NAME', '')
        #     .replace('DOG_AGE', '')
        # )
        # --- END CUSTOM ---

        html_page = html_page.replace(
            '<!--BODY-->', (toc if sorted_meta else '')
        )

    outfile.write_text(html_page)

# --- end if __main__ ---
