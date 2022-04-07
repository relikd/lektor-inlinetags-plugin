# lektor plugin: inlinetags

The inlinetags plugin allows you to use tags inside normal text / html / markdown elements.
For example, you can write `This is my {{Lektor}} powered website` and it will automatically replace the tag with a link to the actual page: `This is my <a href="/tag/lektor/">Lektor</a> powered website`.

Of course, you can configure a different matching pattern, e.g., instead of the default `{{tag}}` use `$tag$` (`\$(.{1,20}?)\$`).

This plugin is based on the [lektor-groupby](https://github.com/relikd/lektor-groupby-plugin) plugin.
All configuration options from groupby can be used (including multiple attribute names).


### Known issues

In rare cases, clicking on "Save Changes" will not replace the tags of the current page.
It happens because the page is built concurrently (race condition).
This affects only the currently edited page and only the inline replacements (the tags page is updated just fine).
If this occurs to you, simply edit and save the page again.


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
slug = "tag/{}/index.html".format(this.key)
template = tag-page.html

[inlinetags.pattern]
match = {{([^}]{1,32})}}
replace = <a href="/tag/{key}/">{name}</a>

[inlinetags.fields]
title = "Tagged: " ~ this.group

[inlinetags.key_map]
C# = c-sharp
```
