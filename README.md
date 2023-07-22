# xml-safe-mod

A small utility for safely making updates to XML configuration files.

It aims to give a safer alternative to using sed when updating XML configuration files, both by avoiding leaking secrets and by making the updates themselves safe and atomic.

## Usage

```sh
# In-place update
echo '{"secret1": "password1"}' | xml-safe-mod --src /etc/daemon/config.xml --in-place --set secret1 ./xpath/expression
# Use a template file to generate another file
echo '{"secret1": "password1"}' | xml-safe-mod --src /etc/daemon/config.xml.in --dest /etc/daemon/config.xml --owner daemon --group daemon --perms 600 --set secret1 ./xpath/expression
```

It supports the [ElementTree subset of XPath](https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax).

## Supported versions of Python

If you need to use this on older versions of Python, such as 3.5 or 3.6, there's nothing specific to it that should stop you from running it. If you remove the type annotations, it should work on any Python 3 release. However, the only versions officially supported are 3.7+ due to the needs of Hatch and the versions of Python available on Github Actions.
