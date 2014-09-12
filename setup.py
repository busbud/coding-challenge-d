from setuptools import setup, find_packages

setup(
    name='coding-challenge-backend-d',
    description='An application to concurrently process images.',
    install_requires=['Pillow'],
    packages=find_packages(exclude=[]),
    entry_points="""\
    [console_scripts]
     challenge-run = app:script
    """
)
