# lektor plugin: inlinetags

The inlinetags plugin allows you to use tags inside normal text / html / markdown elements.
For example, you can write `This is my {{Lektor}} powered website` and it will automatically replace the tag with a link to the actual page: `This is my <a href="/tag/lektor/">Lektor</a> powered website`.

Of course, you can configure a different matching pattern, e.g., instead of the default `{{tag}}` use `$tag$` (`\$(.{1,20}?)\$`).

This plugin is based on the [lektor-groupby](https://github.com/relikd/lektor-groupby-plugin) plugin.
All configuration options from groupby can be used (including multiple attribute names).
Further, you can access the tags of a page with the filter `|vgroups(key1, key2, recursive=False)` where key is `0..N` attribute keys.
If no key is provided, all attributes will be returned – otherwise only matching attribute keys.


### Example config file

Add a new `inlinetags = True` attribute to your model, e.g., a flow block:

```ini
[block]
name = Text Element
button_label = [[paragraph]]

[fields.content]
label = Text
type = markdown
inlinetags = True
```

In your plugin config (`configs/inlinetags.ini`):

```ini
[inlinetags]
root = /
slug = tag/{key}/
template = tag-page.html

[inlinetags.pattern]
match = {{([^}]{1,32})}}
replace = <a class="tag" href="{url}">{name}</a>

[inlinetags.fields]
title = "Tagged: " ~ this.key_obj

[inlinetags.key_map]
C# = c-sharp
```
