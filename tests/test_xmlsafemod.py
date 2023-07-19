import io
import typing as t
import xml.etree.ElementTree as et  # noqa: N813

import xmlsafemod


def apply_modify_document(
    src: str,
    secrets: t.Mapping[str, str],
    changes: t.Sequence[t.Sequence[str]],
) -> str:
    doc = et.ElementTree(et.fromstring(src))  # noqa: S314
    xmlsafemod.modify_document(doc, secrets, changes)
    result = io.StringIO()
    doc.write(result, encoding="unicode")
    return result.getvalue()


def test_empty_document():
    result = apply_modify_document("<stuff/>", {}, [])
    assert result == "<stuff />"


def test_missing_secret():
    result = apply_modify_document(
        "<stuff><login><username>fred</username></login></stuff>",
        {"foo": "baz"},
        [["bar", "./login/username"]],
    )
    assert result == "<stuff><login><username>fred</username></login></stuff>"


def test_nested_secret():
    result = apply_modify_document(
        "<stuff><login><username>fred</username></login></stuff>",
        {"foo": "baz"},
        [["foo", "./login/username"]],
    )
    assert result == "<stuff><login><username>baz</username></login></stuff>"


def test_repeated_secret():
    result = apply_modify_document(
        "<stuff><login><username>fred</username></login><profile>barney</profile></stuff>",
        {"foo": "baz"},
        [["foo", "./login/username", "./profile"]],
    )
    assert result == "<stuff><login><username>baz</username></login><profile>baz</profile></stuff>"
