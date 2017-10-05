# Copyright 2017 Steve Milner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
"""
Reads and provides all known registries configured on a system.
"""

import os

import json
import toml
import yaml


class Registry:
    """
    Registry abstraction.
    """

    def __init__(self, url, from_file, options=None):
        """
        Initializes a new instance of Registry.
        """
        if options is None:
            options = {}
        self.url = url
        self.from_file = from_file
        self.sigstore = options.get('sigstore')
        self.sigstore_staging = options.get('sigstore-staging')
        self.secure = options.get('secure')

    def __repr__(self):
        """
        Instance representation.
        """
        return (
            '<url={}, sigstore={}, from_file={}, sigstore_staging={} '
            'secure={}>'.format(
                self.url, self.sigstore, self.from_file,
                self.sigstore_staging, self.secure))

    __str__ = __repr__


class Registries:
    """
    Manager which loads and provides registry information.
    """

    def __init__(
            self, docker_sysconfig='/etc/sysconfig/docker',
            containers_registries='/etc/containers/registries.d/',
            daemon_json='/etc/docker/daemon.json',
            crio_conf='/etc/crio/crio.conf'
            ):
        """
        Initializes a new instance of Registries.
        """
        self.docker_sysconfig = docker_sysconfig
        self.containers_registries = containers_registries
        self.daemon_json = daemon_json
        self.crio_conf = crio_conf
        self._registries = {}
        self.reload()

    @property
    def registries(self):
        """
        Public access to _registries.
        """
        return self._registries

    @property
    def json(self):
        """
        json representation of the registries.
        """
        class RegistryEncoder(json.JSONEncoder):
            def default(self, i):
                return i.__dict__

        return RegistryEncoder().encode(self._registries)

    def reload(self):
        """
        Reloads from all provided data stores.
        """
        self._load_containers_registries()
        self._load_sysconfig()
        self._load_daemon_json()
        self._load_crio()

    def _load_containers_registries(self):
        """
        Loads registry information from the containers registries.d directory.
        """
        for afile in os.listdir(self.containers_registries):
            from_file = self.containers_registries + afile
            with open(from_file, 'r') as containers_registries:
                data = yaml.load(containers_registries)
                try:
                    for url, opts in data.get('docker').items():
                        opts['secure'] = True
                        registry = Registry(
                            url=url,
                            from_file=from_file,
                            options=opts)
                        self._registries[url] = registry
                except AttributeError:
                    # There are no registries to parse
                    pass

    def _load_sysconfig(self):
        """
        Loads registry information from a docker sysconfig file.
        """
        with open(self.docker_sysconfig, 'r') as dl:
            for line in dl.readlines():
                if line.startswith('ADD_REGISTRY'):
                    # skip the formatting items
                    registries = line[29:-2].split(',')
                    for registry in registries:
                        self._registries[registry] = Registry(
                            url=registry,
                            from_file=self.docker_sysconfig,
                            options={'secure': True})

                if line.startswith('INSECURE_REGISTRY'):
                    registries = line[34:-2].split(',')
                    for registry in registries:
                        self._registries[registry] = Registry(
                            url=registry,
                            from_file=self.docker_sysconfig,
                            options={'secure': False})

    def _load_daemon_json(self):
        """
        Loads registry information from a docker daemon.json file.
        """
        with open(self.daemon_json, 'r') as daemon_json:
            data = json.load(daemon_json)
            for registry in data.get('add-registry', []):
                self._registries[registry] = Registry(
                    url=registry,
                    from_file=self.daemon_json,
                    options={'secure': True}
                )
            for registry in data.get('insecure-registries', []):
                self._registries[registry] = Registry(
                    url=registry,
                    from_file=self.daemon_json,
                    options={'secure': False}
                )

    def _load_crio(self):
        """
        Loads registry information from a cri-o configuration file.
        """
        with open(self.crio_conf, 'r') as crio_conf:
            data = toml.load(crio_conf)['crio']['image']
            for registry in data.get('registries', []):
                self._registries[registry] = Registry(
                    url=registry,
                    from_file=self.crio_conf,
                    options={'secure': True}
                )
            for registry in data.get('insecure_registries', []):
                self._registries[registry] = Registry(
                    url=registry,
                    from_file=self.crio_conf,
                    options={'secure': False}
                )


if __name__ == '__main__':
    print(Registries(
        crio_conf='crio.conf',
        docker_sysconfig='/etc/sysconfig/docker-latest',
        daemon_json='daemon.json').json)
