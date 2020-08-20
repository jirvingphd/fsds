#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# requirements = ['scikit-learn','matplotlib','fsds_100719','statsmodels']

# setup_requirements = [ ]

# test_requirements = [ ]
requirements = ['numpy>=1.18','missingno', 'pandas>=1.0.0', 'seaborn>0.10.0', 'matplotlib>=3.2.2', 'scikit-learn>=0.23.1', 
'scipy','IPython','ipywidgets','tzlocal','pyperclip','cufflinks>=0.17.0']#'tensorflow>2.1.0','keras'] 
#'pytz','tzlocal','gensim','openpyxl','beautifulsoup4',
setup_requirements = [ 'IPython','missingno',*requirements]

test_requirements = ['IPython' ,'ipywidgets','statsmodels',]
test_requirements.extend(requirements)

setup(
    author="James Irving",
    author_email='james.irving.phd@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Cohort agnostic version of fsds_100719 package",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fsds',
    name='fsds',
    packages=find_packages(include=['fsds', 'fsds.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jirvingphd/fsds',
    version='0.2.23',
    zip_safe=False,
)
