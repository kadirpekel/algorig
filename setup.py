from setuptools import setup, find_packages

setup(
    name='algorig',
    py_modules=['algorig'],
    version='0.0.4',
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
    tests_require=[
        'pytest>=1.8.2'
    ],
    entry_points={
        'console_scripts': [
            'rig=algorig.cli:main',
        ],
    },
)
