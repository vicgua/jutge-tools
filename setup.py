from setuptools import setup, find_packages

setup(
    name='jutge-tools',
    version='2.0.0a0',
    packages=find_packages(),
    package_data={
        'JutgeTools': ['data/*']
    },
    python_requires='>=3.4',
    install_requires=[
        'attrs',
        'lxml',
        'requests',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'jutge-tools = JutgeTools.__main__:main'
        ]
    }
)
