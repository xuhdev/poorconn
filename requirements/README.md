This directory manages dependencies for testing and development environments. Their versions are fixed in the various
`*.txt` files, which are generated by `pip-compile` on the `*.in` files. Run `tox -e dep-update` to regenerate the
`*.txt` files, with packages in it updated to their latest versions.
