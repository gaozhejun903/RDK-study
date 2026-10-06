from setuptools import setup

package_name = 'rdk_study_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='RDK-study',
    maintainer_email='example@example.com',
    description='RDK-study beginner control examples',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'number_publisher = rdk_study_control.number_publisher:main',
            'number_subscriber = rdk_study_control.number_subscriber:main',
            'square_driver = rdk_study_control.square_driver:main',
        ],
    },
)
