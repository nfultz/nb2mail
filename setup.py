from setuptools import setup

setup(name='nb2mail',
      version='1.0',
      description='Convert notebooks to email',
      url='http://github.com/nfultz/nb2mail',
      download_url='https://github.com/nfultz/nb2mail/tarball/0.8',
      author='Neal Fultz',
      author_email='nfultz@gmail.com',
      license='BSD',
      packages=['nb2mail'],
      install_requires=['nbconvert>=6.0.0'],
      zip_safe=False,
      include_package_data=True,
      entry_points = {
          'nbconvert.exporters': [
              'mail = nb2mail:MailExporter',
          ],
          'nbconvert.postprocessors': [
              'sendmail = nb2mail:SendMailPostProcessor',
          ]
      }
)
