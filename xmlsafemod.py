#!/usr/bin/env python3

"""
A utility for safely making updates to XML configuration files.

Copyright (c) Keith Gaughan, 2023.
This software is provided under the terms of the MIT license. See LICENSE
for full details.

Repo: https://github.com/kgaughan/xml-safe-mod
"""

import argparse
import grp
import json
import os.path
import pwd
import sys
import tempfile
import typing as t
import xml.etree.ElementTree as et  # noqa: N813

__version__ = "0.1.1"


def get_uid(user_name: str, default: int) -> int:
    if user_name is not None:
        try:
            return pwd.getpwnam(user_name).pw_uid
        except KeyError:
            print(f"WARNING: no such user '{user_name}'", file=sys.stderr)
    return default


def get_gid(group_name: str, default: int) -> int:
    if group_name is not None:
        try:
            return grp.getgrnam(group_name).gr_gid
        except KeyError:
            print(f"WARNING: no such group '{group_name}'", file=sys.stderr)
    return default


def modify_document(
    root: et.ElementTree,
    secrets: t.Mapping[str, str],
    changes: t.Sequence[t.Sequence[str]],
):
    # Replace all the secrets in the XML file.
    for change in changes:
        # We skip anything without a match for no paths.
        if change[0] not in secrets or len(change) == 1:
            continue
        # For each path, substitute the secret.
        for path in change[1:]:
            for elem in root.findall(path):
                elem.text = secrets[change[0]]


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A utility for safely making updates to XML configuration files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--src",
        help="Source file to generate configuration",
        required=True,
    )

    dest_grp = parser.add_mutually_exclusive_group(required=False)
    dest_grp.add_argument(
        "--dest",
        help="Destination file for generated configuration",
    )
    dest_grp.add_argument(
        "--in-place",
        help="Overwrite --src",
        action="store_true",
    )

    parser.add_argument(
        "--owner",
        help="Owner for resulting file",
    )
    parser.add_argument(
        "--group",
        help="Group to own resulting file",
    )
    parser.add_argument(
        "--perms",
        type=lambda x: int(x, 8),
        default="600",
        help="Permissions to use",
    )

    parser.add_argument(
        "--set",
        metavar="S",
        nargs="+",
        help="Secret name and list of XPath definitions of where to write it",
        action="append",
    )
    return parser


def main():
    args = make_parser().parse_args()
    secrets = json.load(sys.stdin)

    with open(args.src, encoding="UTF-8") as fh:
        root = et.parse(fh)  # noqa: S314

    modify_document(root, secrets, args.set or ())

    dest = args.src if args.in_place else args.dest

    # Write the document to a temporary file in the same directory. This allows
    # the move to be atomic.
    tmp_fd, tmp_name = tempfile.mkstemp(dir=os.path.dirname(dest))
    with os.fdopen(tmp_fd, mode="w", encoding="UTF-8") as fh:
        root.write(fh, encoding="unicode", xml_declaration=True)
        fh.write("\n")

    # Set permissions.
    os.chmod(tmp_name, args.perms)

    # Copy ownership from source if nothing's explicitly given.
    statinfo = os.stat(args.src)
    uid = get_uid(args.owner, statinfo.st_uid)
    gid = get_gid(args.group, statinfo.st_gid)
    os.chown(tmp_name, uid, gid)

    os.replace(tmp_name, dest)


if __name__ == "__main__":
    main()
