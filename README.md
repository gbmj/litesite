# litesite.py

## Generate a static site for a blog-like collection of pages.

litesite gives you nearly total freedom to design your site. The
script simply stitches together repeated content, such as headers,
sidebars and footers, with page-specific content. How you structure
those elements is up to you. The purpose is to reduce the work of
tweaking something that repeats across many pages: change it in
just one place, and it propagates to all relevant pages on your
next build.

### Examples
Visit https://github.com/gbmj/gbmj-net to see three distinct litesite scripts running on a main site plus two subsites.

### How to Use
Copy litesite.py into the root folder for the files you want to
build and edit the USER SETTINGS section. Create your common and
page-specific input files (see [Assumed folder structure](#assumed-file--folder-structure)),
using content placeholders where desired (see [Placeholders](#placeholders)). Feel
free to add custom logic to process your own tags and placeholders;
the script indicates where such logic is needed.

Use your preferred package manager to install the script's external
dependencies (see [Requirements](#requirements)), update the shebang line as needed,
and run.

### Requirements
- python 3.13 or later
- pypandoc 1.15 or later (plus pandoc 3.8 or later),
see https://pypi.org/project/pypandoc/
- python-frontmatter 1.1 or later, see https://pypi.org/project/python-frontmatter/
- the common head, pre and post files must contain valid html; the
script will insert them as is. The common head file must begin
and end with `<head>` resp `</head>`.
- you can use any file extension you like for your input files,
including one you made up, but the actual content must be in
a pandoc-supported input format. See https://pandoc.org/MANUAL.html#options.
- all input files you want the script to process must include a
YAML frontmatter block containing `litesite:`. Files without this
tag will be ignored.

### Assumed file & folder structure
```
litesite.py         (this file; required)
*.foo               (0+ input files; ext customizable)
*.*                 (0+ other files/folders)
cmn/                (required; name customizable)
|_ head.html        (required; name customizable)
|_ cpre.html        (required; name customizable)
|_ cpost.html       (required; name customizable)
|_ npre.html        (optional; name customizable)
|_ npost.html       (optional; name customizable)
*/                  (0+ other folders)
|_ *.foo            (0+ input files)
|_ *.*              (0+ other files)
|_ */               (0+ subfolders with similar structure)
```

The script generates an html page for each input file in the root
folder plus subfolders up to `MAXDEPTH` (customizable). Each html
page uses the name of its input file. Example:
`coolest-page-ever.foo` will generate `coolest-page-ever.html`.

The script distinguishes between standalone pages and pages that
are part of a Collection. You tell the script which is which
using YAML frontmatter:
- input files tagged `litesite: collection` generate Collection pages.
- input files tagged `litesite:` with any other value (including
an empty string) generate standalone pages.
- input files with no `litesite:` tag do not generate html pages.
This means you can also use the chosen extension for other things.

Collection pages use the `cpre` and `cpost` files; standalone pages
use `npre` and `npost`. This allows you to tailor the common elements
to the page type. If you want all pages to have the same common parts,
set the same filenames for both in USER SETTINGS.

The home page is a special case. If there is no top-level `index.foo`,
the script will create the page from scratch, using `cpre` and `cpost`
and adding a table of contents (TOC) listing the Collection. If
`index.foo` does exist, the script will build a regular standalone page,
then scan the result for a TOC placeholder (see [Placeholders](#placeholders)). If found,
the script inserts a TOC at this location.

### Styling the TOC
The generated table of contents includes a title, optional subtitle,
optional year headings, and a list of links to pages in the Collection,
with or without descriptive blurbs. Because the TOC is
generated and not under your direct control, the script provides
three customizable css classes so you can fine-tune its styling.
See USER SETTINGS in the script.

### Optional frontmatter
In addition to the required `litesite:`, the script recognizes
three optional frontmatter tags:

- `title:` Title of Page
- `date:` YYYY-MM-DD
- `blurb:` A short summary to use in the table of contents.

The date can be any valid ISO 8601 timestamp with at least the
fields shown above. You don't need to wrap the title or blurb in
quote marks, but you may. The tags can be in any order and additional
frontmatter is fine; the script will ignore it (unless you add logic
to handle it; see [Custom tags and placeholders](#custom-tags-and-placeholders).)

For missing tags, the script defaults to:

- `title:` Titlecased Name Of File With Dashes Converted To Spaces
- `date:` 0001-01-01
- `blurb:` ''

(For files named `index`, the script defaults to the name of the
enclosing folder.)

### Placeholders
The script offers several out-of-the-box placeholders you can
use in your `head`, `pre`, `post` and `.foo` files. You can also create
your own. The naming convention is meant to help you
produce valid html:

- `*_TEXT_PH` - use anywhere ordinary text is valid
- `*_URL_PH` - of the form `https://bar.foo/baz`; use anywhere
a full web address including protocol is valid
- `*_LINK_PH` - of the form
`<a href="https://bar.foo/baz">previous</a>`;
use anywhere a complete anchor element is valid

#### List of standard placeholders
In the list below, (scope) indicates the pages on which the
script will process the given placeholder. If you use a
placeholder outside its scope, it will still be there in the
final page (unless you modify the script to handle it).

|scope|placeholder|description|
|------|---------|---------------------------|
|(any)|`DOMAIN_URL_PH`, `HOME_URL_PH`| a convenience for converting relative links to absolute. Note, these URLs contain a trailing slash, so proper use will look funny: For example, write `<img href="DOMAIN_URL_PHimages/me.png" />` and not `<img href="DOMAIN_URL_PH/images/me.png" />`.|
|(any)|`NAME_DOMAIN_TEXT_PH`, `SITENAME_TEXT_PH`|insert the name of the overarching domain resp. this site. Useful for subsites that point back to the main site.
|(any)|`SELF_URL_PH`|insert the absolute URL to the current page. Exclusively for a rel="canonical" link in your head file. The script disables all other self-links on a page.|
|(any)|`YEAR_TEXT_PH`, `DATE_TEXT_PH`|insert the year resp. full date specified in the page's frontmatter (else the default value). Note, the date will be in ISO 8601 format. Modify the script if you want something prettier :).|
|(any)|`TITLE_TEXT_PH`|insert the title specified in the page's frontmatter (else the default value). Use in the head file's `<title></title>` element (and elsewhere as you desire).|
|(coll)|`PREV_URL_PH`, `NEXT_URL_PH`|insert URLs to the page's TOC neighbors. Note, for nav links in headers, sidebars etc. you might prefer the `_LINK_` versions below.|
|(coll, home w/no `.foo` file)|`PREV_LINK_PH`, `HOME_LINK_PH`, `NEXT_LINK_PH`|insert the entire anchor element for the page's TOC neighbors resp. the home page. Use these instead of the `_URL_` placeholders to 'gray out' nav links that shouldn't be active: the TOC link on the home page itself, and the previous resp. next links on the first resp. last pages in the Collection.|
|(home with `.foo` file)|`TOC_BLOCK_PH`|insert a table of contents listing the Collection, with links to each page. Only active on the site's home page, and only if there's a corresponding `index.foo` file.

### Custom tags and placeholders:
You can process custom frontmatter tags and/or placeholders by
adding the required logic where indicated in the script comments.

### Tips:
The script starts from the directory you run it in and creates a
self-contained site -- so you could run separate copies in several
folders on your domain, creating multiple self-contained collections
with their own styling and navigation. If you do that, be sure to
set `MAXDEPTH` so you don't overwrite files in subfolders where you're
running the script independently. If you need to process files in
some subfolders but want others to run independently, use different
file extensions for each site. See an example of the latter at
https://github.com/gbmj/gbmj-net.

You can create a non-blog-like site simply by omitting
blog-like navigation placeholders (those with `PREV`, `NEXT`, `TOC`) and
using the same pre and post files for all pages, or by having
no input files with `litesite: collection` in the frontmatter.

If you write your content in markdown: pandoc supports a whole
lot of fancy stuff out of the box (fenced code, header attributes,
definition lists, pipe tables, ...) without extra options or
extensions, if you use 'markdown' as your input format. See
https://pandoc.org/MANUAL.html#pandocs-markdown.

### Limitations:
This script is only aware of page-level common elements:
their contents are inserted between the `<body>` and `<main>` (
resp. `</main>` and `</body>`) tags. If you need section-level headers,
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
- the generated TOC is hardcoded to use `h1` for its title,
`p` for its subtitle, and `ul` for its contents.
Modify the script if you prefer different behavior.

#### Licensed under GPLv3.(c) 2025 Grayson Bray Morris