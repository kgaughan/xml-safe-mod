# xml-safe-mod

A small utility for safely making updates to XML configuration files.

It aims to give a safer alternative to using sed when updating XML configuration files, both by avoiding leaking secrets and by making the updates themselves safe and atomic.

## Usage

```sh
# In-place update
echo '{"secret1": "password1"}' | xml-safe-mod --src /etc/daemon/config.xml --in-place --set secret1 ./xpath/expression
# Use a template file to generate another file
echo '{"secret1": "password1"}' | xml-safe-mod --src /etc/daemon/config.xml.in --dest /etc/daemon/config.xml --owner daemon --group daemon --perms 600 --set secret1 ./xpath/expression
# Use a configuration file instead:
echo '{"secret1": "password1"}' | xml-safe-mod --config /etc/daemon/xml-safe-mod.json
```

The configuration file would look something like this:

```json
{
  "src": "/etc/daemon/config.xml.in",
  "dest": "/etc/daemon/config.xml",
  "owner": "daemon",
  "group": "daemon",
  "perms": 600,
  "set": {
    "secret1": [
      "./xpath/expression"
    ]
  }
}
```

It would support the [ElementTree subset of XPath](https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax).
