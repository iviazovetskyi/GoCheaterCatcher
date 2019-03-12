from setuptools import setup

setup(name='GoCheaterCatcher',
      version='0.1',
      description='Analysis of .sgf with .asgf output for further analysis',
      url='https://github.com/IgorBS/GoCheaterCatcher',
      author='Igor Burnaevskiy',
      author_email='igor_bs@mail.ru',
      python_requires='>=2.7',
      license='MIT',
      packages=['GoCheaterCatcher'],
	  #install_requires=[
      #  'gomill'],
      #dependency_links=['https://github.com/leela-zero/leela-zero'],
      zip_safe=False)