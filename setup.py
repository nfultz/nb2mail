from setuptools import setup

setup(name='nb2mail',
      version='0.1',
      description='Convert notebooks to email',
      url='http://github.com/nfultz/nb2mail',
      author='Neal Fultz',
      author_email='nfultz@gmail.com',
      license='BSD',
      packages=['nb2mail'],
      install_requires=['jupyter'],
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
