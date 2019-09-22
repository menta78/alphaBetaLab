from setuptools import setup

setup(
    name='alphaBetaLab',
    version='1.1.0',
    author='Lorenzo Mentaschi',
    author_email='lorenzo.mentaschi@unige.it',
    packages=['alphaBetaLab', 'alphaBetaLab.test', 'alphaBetaLab.plot'],
    install_requires=[
        "numpy >= 1.8.2",
        "shapely >= 1.5.9",
        "basemap",
        "pyproj"
    ],
)
 
