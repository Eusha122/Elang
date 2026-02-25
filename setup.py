from setuptools import setup, find_packages

setup(
    name='elang',
    version='0.1.0',
    description='Eusha Language - A modern, beginner-friendly programming language',
    author='Eusha',
    packages=['elang'],
    entry_points={
        'console_scripts': [
            'elang=elang.elang:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Interpreters',
    ],
)
