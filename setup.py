from setuptools import setup, find_packages

setup(
    name='job_status',
    version='0.1.0',
    description='A package to monitor and store job statuses using SQLite and Rich',
    author='Utpal Kumar',
    author_email='utpalkumar@berkeley.edu',
    url='https://github.com/yourusername/job_status',
    packages=find_packages(),  # Automatically find and include your packages
    install_requires=[
        'rich',        
        'pyyaml',
        'pysqlite3',     
    ],
    package_data={
        'job_status': ['config.yaml'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  
    entry_points={
        'console_scripts': [
            'job-status=job_status.job_monitor:main',  
        ],
    },
)
