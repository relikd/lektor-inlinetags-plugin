# -*- coding: utf-8 -*-
from lektor.markdown import Markdown, Markup
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter, style
from lektor.types.formats import MarkdownDescriptor
from lektor.utils import slugify
import re
from typing import Set, Dict, Iterator, Tuple
from collections import namedtuple

InlineTag = namedtuple('InlineTag', ['slug', 'title', 'link'])


class InlineTagsPlugin(Plugin):
    name = 'InlineTags'
    description = 'Auto-detect and reference tags inside written text.'

    def on_setup_env(self, **extra) -> None:
        def _iter_inlinetags(record, *, children=False) -> Set[InlineTag]:
            res = set()
            if hasattr(record, 'inlinetags'):
                res.update(record.inlinetags.values())
            if children and hasattr(record, 'children'):
                for child in record.children:
                    res.update(_iter_inlinetags(child, children=True))
            return res

        self.env.jinja_env.filters.update(inlinetags=_iter_inlinetags)

    def on_groupby_before_build_all(self, groupby, **extra) -> None:
        # load config
        config = self.get_config()
        root = config.get('root', '/')  # type: str
        temp = config.get('template', 'inlinetag.html')  # type: str
        regex = config.get('regex', r'{{([^}]{1,32})}}')  # type: re.Pattern
        rel_url = config.get('link', 'tags/{tag}/')  # type: str
        link_format = config.get('replace', '<a href="{link}">{title}</a>')  # type: str
        slug_map = config.section_as_dict('slugs')  # type: Dict

        # normalize and validate input
        try:
            regex = re.compile(regex)
        except Exception as e:
            err = 'inlinetags.regex not valid: ' + str(e)
            reporter._write_line(style(err, fg='red'))
            return
        if rel_url.endswith('/index.html'):
            rel_url = rel_url[:-10]
        root = root.rstrip('/') + '/'  # ensure end slash
        abs_url = rel_url if rel_url.startswith('/') else root + rel_url
        rel_url = rel_url.replace('{tag}', '{group}')

        # detect and replace tags
        @groupby.depends_on(self.config_filename)
        @groupby.watch(root, 'inlinetags', slug=rel_url, template=temp)
        def convert_inlinetags(args) -> Iterator[Tuple[str, InlineTag]]:
            arr = args.field if isinstance(args.field, list) else [args.field]
            tmptags = {}  # type: Dict[str, InlineTag]
            for obj in arr:
                if isinstance(obj, (Markdown, MarkdownDescriptor)):
                    obj = obj.source
                if isinstance(obj, str) and str:
                    for match in regex.finditer(obj):
                        title = match.group(1)
                        slug = slug_map.get(title, slugify(title))
                        link = abs_url.replace('{tag}', slug)
                        tmptags[title] = InlineTag(slug, title, link)
                        yield slug, tmptags[title]
                # ignore other types (int, float, date, url, undefined)

            # Create new attribute on page record.
            # All tagged records are guaranteed to have this attribute.
            if not hasattr(args.record, 'inlinetags'):
                args.record.inlinetags = tmptags
            elif tmptags:
                args.record.inlinetags.update(tmptags)

            # replace inline-tags with hyperlink
            if tmptags:
                def _repl_tags(match: re.Match) -> str:
                    inl_tag = tmptags[match.group(1)]
                    return link_format.format(**inl_tag._asdict())

                # get field value
                key, b_idx, b_key = args.key
                obj = args.record[key]
                if b_idx is not None:
                    obj = obj.blocks[b_idx][b_key]

                # type = markdown
                if isinstance(obj, (Markdown, MarkdownDescriptor)):
                    obj.source = regex.sub(_repl_tags, obj.source)
                # type = checkboxes, strings
                elif isinstance(obj, list):
                    for i in range(len(obj)):
                        obj[i] = regex.sub(_repl_tags, obj[i])
                # type = html, select, string, text
                elif isinstance(obj, str):
                    newval = regex.sub(_repl_tags, obj)
                    # type = html
                    if isinstance(obj, Markup):
                        newval = Markup(newval)
                    if b_idx is None:
                        # _data is only writable in source info update
                        # during build, write to _bound_data is necessary
                        args.record._bound_data[key] = newval
                    else:
                        # here, using _data seems fine...
                        args.record[key].blocks[b_idx]._data[b_key] = newval
