from lektor.context import get_ctx
from lektor.markdown import Markup  # isinstance
from lektor.pluginsystem import Plugin  # subclass
import re
from lektor_groupby.util import report_config_error
from typing import TYPE_CHECKING, Set, Dict, Any, Generator
if TYPE_CHECKING:
    from lektor.pluginsystem import IniFile
    from lektor_groupby import GroupBy, GroupByCallbackArgs


class InlineTagsPlugin(Plugin):
    name = 'inlinetags'
    description = 'Auto-detect and reference tags inside written text.'

    def on_process_template_context(self, context: Dict, **extra: Any) -> None:
        if hasattr(context.get('this'), '_inlinetag_modified'):
            ctx = get_ctx()
            if ctx:
                ctx.record_dependency(self.config_filename)

    def on_groupby_before_build_all(self, groupby: 'GroupBy', **extra: Any) \
            -> None:
        ''' lektor-groupby entry point. '''
        self.config_keys = set()  # type: Set[str]
        config = self.get_config()
        for sect in config.sections():
            if '.' in sect:  # e.g., sect.fields and sect.key_map
                continue
            if self._add(sect, config, groupby):
                self.config_keys.add(sect)

    def _add(self, sect_key: str, config: 'IniFile', groupby: 'GroupBy') \
            -> bool:
        ''' Parse config section and add callback. Return True on success. '''
        _pattern = config.section_as_dict(sect_key + '.pattern')
        regex_str = _pattern.get('match', r'{{([^}]{1,32})}}')  # type: str
        tag_replace = _pattern.get('replace', '{name}')  # type: str
        try:
            regex = re.compile(regex_str)
        except Exception as e:
            report_config_error(sect_key, 'pattern.match', regex_str, e)
            return False

        watcher = groupby.add_watcher(sect_key, config)

        @watcher.grouping()
        def _fn(args: 'GroupByCallbackArgs') -> Generator[str, str, None]:
            arr = args.field if isinstance(args.field, list) else [args.field]
            _tags = {}  # type: Dict[str, str]
            for obj in arr:
                if hasattr(obj, 'source'):
                    obj = obj.source
                if isinstance(obj, str) and str:
                    for match in regex.finditer(obj):
                        name = match.group(1)
                        _tags[name] = yield name
                # ignore other types (int, float, date, url, undefined)

            # replace inline-tags with hyperlink
            if _tags:
                def _repl_tags(match: re.Match) -> str:
                    name = match.group(1)
                    return tag_replace.format(key=_tags[name], name=name)

                args.record._inlinetag_modified = True
                # get field value
                key, b_idx, b_key = args.key
                obj = args.record[key]
                if b_idx is not None:
                    obj = obj.blocks[b_idx][b_key]

                # type = markdown
                if hasattr(obj, 'source'):
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
                        # thus, during build, _bound_data is necessary
                        args.record._bound_data[key] = newval
                    else:
                        # here, using _data seems fine...
                        args.record[key].blocks[b_idx]._data[b_key] = newval
        return True
