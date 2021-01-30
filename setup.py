# Copyright (C) 2020--2021  Hong Xu <hong@topbug.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pathlib

import setuptools


setuptools.setup(
    name="poorconn",
    description="Simulating poor network connections.",
    long_description=pathlib.Path("README.rst").read_text(),
    long_description_content_type="text/x-rst",
    keywords="socket, test, unittest",
    author="Hong Xu",
    author_email="hong@topbug.net",
    url="https://poorconn.topbug.net",
    project_urls={
        'Source': 'https://gitlab.com/xuhdev/poorconn',
        'Tracker': 'https://gitlab.com/xuhdev/poorconn/issues'
    },
    license="LGPLv3+",
    packages=setuptools.find_packages(),
    data_files=[("", ["COPYING", "COPYING.GPL"])],
    python_requires=">=3.7",
    extras_require={
        'full': ['pytest >= 6.2'],
    },
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: DFSG approved",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    entry_points={"pytest11": ["poorconn = poorconn.pytest_plugin"]},
    use_scm_version={'write_to': 'poorconn/_version.py'},
    setup_requires=['setuptools_scm']
)
