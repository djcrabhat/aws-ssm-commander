from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aws-ssm-commander',
    version='0.0.4',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    long_description=long_description,
    description="A utility for dealing with AWS SSM Parameter Store",
    long_description_content_type="text/markdown",
    url="https://github.com/djcrabhat/aws-ssm-commander",
    install_requires=[
        'Click',
        'boto3',
        'pyyaml',
        'treelib'
    ],
    entry_points='''
        [console_scripts]
        aws-ssm-commander=ssmcommander.cli:cli
    ''',
)
