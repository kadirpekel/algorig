from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
cwd = Path(__file__).parent
long_description = (cwd / 'README.md').read_text()

setup(
    name='algorig',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['algorig'],
    version='0.0.9',
    python_requires='>3.5.4',
    description='algorand development rig',
    author='Kadir Pekel',
    author_email='kadirpekel@gmail.com',
    packages=find_packages(include=['algorig']),
    url='https://github.com/kadirpekel/algorig',
    install_requires=[
        'py-algorand-sdk>=1.8.0',
        'pyteal==0.9.0',
        'komandr>=2.0.1',
        'gdparser>=0.0.2'
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8'    
        ]
    },
    tests_require=[
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'rig=algorig.cli:main',
        ],
    },
)
