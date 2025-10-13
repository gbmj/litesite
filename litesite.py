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

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "python-frontmatter" = ">=1.1",
#     "pandoc" = ">=3.8",
#     "pypandoc" = ">=1.15",
# ]
# ///

"""Generate a static site for a blog-like collection of pages.

See https://github.com/gbmj/litesite?tab=readme-ov-file for
detailed documentation.
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
    """Replace `current` values with `new` if present, ignoring keys not
    already in `current`."""
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
