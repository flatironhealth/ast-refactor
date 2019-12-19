#!/usr/bin/env xonsh
$PROJECT = 'ast-refactor'
$ACTIVITIES = [
	'version_bump',
	'tag',
	'pypi',
	'push_tag',
	'ghrelease'
]

$GITHUB_ORG = 'flatironhealth'
$GITHUB_REPO = 'ast-refactor'

$VERSION_BUMP_PATTERNS = [
   # These note where/how to find the version numbers
   ('ast_refactor/__init__.py', '__version__\s*=.*', '__version__ = "$VERSION"'),
   ('setup.py', 'version\s*=.*,', 'version="$VERSION",'),
   ('Dockerfile', 'LIBRARY_VERSION.*', 'LIBRARY_VERSION $VERSION'),
   ('conda.recipe', 'version:\s*:.*', 'version: "$VERSION"'),
]
