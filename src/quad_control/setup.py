from setuptools import find_packages, setup

package_name = 'quad_control'

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
    maintainer='riasathasan',
    maintainer_email='riasathasan@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'voice_control = quad_control.voice_control_node:main',
        'telemetry_gui = quad_control.telemetry_gui_node:main',
        'mode_manager = quad_control.mode_manager_node:main',
        'leader_follower = quad_control.leader_follower_node:main',
    ],
},
)
