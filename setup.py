from setuptools import setup

setup(name='trading_bot',
      version='0.3.0',
      install_requires=[
            'pandas',
            'numpy',
            'psycopg2-binary',
            'tqdm',
            'pyhumps',
            'pandas-ta'
      ]
)