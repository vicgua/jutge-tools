from setuptools import setup, find_packages

setup(
    name='jutge-tools',
    version='1.0.1',
    packages=find_packages(),
    python_requires='~=3.5',
    entry_points={
        'console_scripts': [
            'jutge-tools = JutgeTools.cli:main'
        ]
    }
)