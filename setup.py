from setuptools import setup, find_packages

setup(
    name='jutge-tools',
    version='1.2.2',
    packages=find_packages(),
    package_data={
        'JutgeTools': ['data/*']
    },
    python_requires='>=3.4',
    install_requires=[
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'jutge-tools = JutgeTools.__main__:main'
        ]
    }
)
