# -*- coding: utf-8 -*-
import re
from typing import List, Tuple
from lektor.context import get_ctx
from lektor.db import Page
from lektor.markdown import Markdown
from lektor.pluginsystem import Plugin
from lektor.types.flow import Flow, FlowBlock, FlowDescriptor
from lektor.types.formats import MarkdownDescriptor
from lektor.utils import slugify

_regex = re.compile(r'{{[^}]{1,32}}}')
_tag_repl: List[Tuple[str, str]] = []


def tagify(text):
    for old, new in _tag_repl:
        text = text.replace(old, new)
    return slugify(text)


def _recursive_tags(obj):
    res = {}
    source = [obj]
    while source:
        x = source.pop()
        if isinstance(x, Markdown):
            res.update(x.meta['tags'])
        elif isinstance(x, FlowBlock) or isinstance(x, Page):
            for key, field in x._data.items():
                if isinstance(field, Markdown):
                    source.append(field)
                elif isinstance(field, (MarkdownDescriptor, FlowDescriptor)):
                    source.append(x[key])
        elif isinstance(x, Flow):
            source.extend(x.blocks)
        else:
            print(type(x))
    return res.items()


class AutoTagMixin(object):
    def _replace_tag(self, match):
        title = match.group()[2:-2]
        slug = tagify(title)
        self.meta['tags'][slug] = title
        return self.meta['tag_template'].format(tag=slug, title=title)

    def text(self, text):
        return _regex.sub(self._replace_tag, super().text(text))


# Wrapper with an __html__ method prevents
# Lektor from escaping HTML tags.
class HTML(object):
    def __init__(self, html):
        self.html = html

    def __html__(self):
        return self.html


class Main(Plugin):
    def _to_tag(self, title, slug=None):
        if not slug:
            slug = tagify(title)
        get_ctx().record_dependency(self.config_filename)
        return HTML(self.tag_template.format(tag=slug, title=title))

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update(
            make_tag=self._to_tag
        )
        self.env.jinja_env.filters.update(
            tags=_recursive_tags
        )

    def on_before_build_all(self, builder, **extra):
        global _tag_repl
        config = self.get_config()
        self.tag_template = config.get('template', '{title}')
        _tag_repl = config.section_as_dict('replace').items()

    def on_markdown_config(self, config, **extra):
        config.renderer_mixins.append(AutoTagMixin)

    def on_markdown_meta_init(self, meta, record, **extra):
        meta['tags'] = {}
        meta['tag_template'] = self.tag_template

    def on_markdown_meta_postprocess(self, meta, record, **extra):
        if meta['tags']:
            get_ctx().record_dependency(self.config_filename)
