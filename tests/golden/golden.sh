#!/bin/sh

set -eu

here="$(dirname "$0")"
for input in "$here"/*.in.xml; do
	golden="${input%%.in.xml}.out.xml"

	dest="$(mktemp "${TMPDIR:-/tmp}"/tmp.golden.XXXXXXXX.xml)"
	python3 -m xmlsafemod \
		--set username "./uname" "./delegate/profile" \
		--set password "./pwd" \
		--src "$input" --dest "$dest" < "$here"/creds.json

	if ! cmp -s "$dest" "$golden"; then
		echo "Found difference between golden file '$golden' and '$input' when processed:"
		diff -u "$golden" "$dest"
		exit 1
	fi
done
