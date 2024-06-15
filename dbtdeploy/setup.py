from setuptools import setup, find_packages

setup(
    name='dbtdeploy',
    version='0.1',
    description='foo',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # dbt core library
        'dbt-core',
        # dbt plugins, choose as required
        'dbt-sqlite',
        #'dbt-sqlserver'
    ],
)
