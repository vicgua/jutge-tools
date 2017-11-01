from setuptools import setup, find_packages

setup(
    name='jutge-tools',
    version='1.1.2',
    packages=find_packages(),
    python_requires='>=3.4',
    entry_points={
        'console_scripts': [
            'jutge-tools = JutgeTools._aux.cli:main'
        ]
    }
)