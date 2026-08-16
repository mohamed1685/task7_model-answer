from setuptools import find_packages, setup

package_name = 'group_task_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohamed-amr',
    maintainer_email='mohamed.amr9327@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'movement_node = group_task_pkg.movement_node:main',
            'control_node = group_task_pkg.control_node:main',

        ],
    },
)
