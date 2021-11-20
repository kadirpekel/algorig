from setuptools import setup

setup(
    name='algorig',
    py_modules=['algorig'],
    version='0.0.1',
    description='algorand development rig',
    author='Kadir Pekel',
    author_email='kadirpekel@gmail.com',
    url='https://github.com/kadirpekel/algorig',
    install_requires=[
        'py-algorand-sdk>=1.8.0',
        'pyteal==0.9.0',
        'komandr>=1.0.4',
    ],
    tests_require=[
        'pytest>=1.8.2'
    ],
    entry_points={
        'console_scripts': [
            'rig=algorig.cli:main',
        ],
    },
)
