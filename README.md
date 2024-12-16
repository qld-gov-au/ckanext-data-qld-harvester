# ckanext-harvester-data-qld-geoscience

A CKAN extension to implement custom harvesting requirements for Data.Qld.

## Installation

* Activate your virtual environment
```
. /usr/lib/ckan/default/bin/activate
```
* Install the extension
```
pip install 'git+https://github.com/qld-gov-au/ckanext-harvester-data-qld-geoscience.git#egg=ckanext-harvester-data-qld-geoscience'
```
> **Note**: If you prefer, you can download the source code as well and install in 'develop' mode for easy editing. To do so, use the '-e' fla
g:
> ```
> pip install -e 'git+https://github.com/qld-gov-au/ckanext-harvester-data-qld-geoscience.git#egg=ckanext-harvester-data-qld-geoscience'
> ```

* Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `harvest` and `harvester_data_qld_geoscience` in the `ckan.plugins` property.
```
ckan.plugins = <OTHER_PLUGINS> harvest harvester_data_qld_geoscience
```

## Tests

- Make sure that you have latest versions of all required software installed:
  - [Docker](https://www.docker.com/)
  - [Pygmy](https://pygmy.readthedocs.io/)
  - [Ahoy](https://github.com/ahoy-cli/ahoy)

- Build the test container for your preferred CKAN version: '2.9' or '2.10'.
```
CKAN_VERSION=2.10 bin/build.sh
```

- Run tests:
```
bin/test.sh
bin/test.sh
```
