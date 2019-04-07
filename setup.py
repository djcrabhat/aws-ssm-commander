from setuptools import setup, find_packages

setup(
    name='aws-ssm-commander',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'boto3',
        'pyyaml',
        'treelib'
    ],
    entry_points='''
        [console_scripts]
        ssm-commander=ssmcommander.cli:cli
    ''',
)