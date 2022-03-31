# lektor plugin: inlinetags

### Default config file

```ini
root = /
template = inlinetag.html
regex = {{([^}]{1,32})}}
link = tags/{tag}/
replace = <a href="{link}">{title}</a>

[slugs]
C# = c-sharp
```