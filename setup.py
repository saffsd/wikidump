from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.3'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='wikidump',
    version=version,
    description="Tools to manipulate and extract data from wikipedia dumps",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      "Development Status :: 3 - Alpha"
    , "Environment :: Console"
    , "Intended Audience :: Science/Research"
    , "License :: OSI Approved :: GNU General Public License (GPL)"
    , "Operating System :: OS Independent"
    , "Programming Language :: Python"
    , "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    keywords='wikipedia',
    author='Marco Lui',
    author_email='saffsd@gmail.com',
    url='http://github.com/saffsd/wikidump',
    license='GPL3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['wikidump=wikidump:main']
    }
)
