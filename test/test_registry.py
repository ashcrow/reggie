
import json

import pytest

from reggie import Registry


class TestRegistry:
    """
    Tests for the registry class.
    """

    def test_init_without_options(self):
        """
        Verify Registry data when no options are passed.
        """
        url = 'example.org:500'
        from_file = 'afile'
        reg = Registry(url=url, from_file=from_file)

        assert reg.url == url
        assert reg.from_file == from_file
        assert reg.secure is None
        assert reg.sigstore is None
        assert reg.sigstore_staging is None

    def test_init_with_options(self):
        """
        Verify Registry data when options are provided.
        """
        url = 'example.org:500'
        from_file = 'afile'
        options = {
            'secure': False,
            'sigstore': 'test',
            'sigstore-staging': 'test',
        }
        reg = Registry(url=url, from_file=from_file, options=options)

        assert reg.url == url
        assert reg.from_file == from_file
        for key in options:
            assert getattr(reg, key.replace('-', '_')) == options[key]

    def test_repr(self):
        """
        Verify a nice representation of the instance is provided for printing.
        """
        url = 'example.org:500'
        from_file = 'afile'
        reg = Registry(url=url, from_file=from_file)

        printable = reg.__repr__()
        assert 'url={}'.format(url) in printable
        assert 'from_file={}'.format(from_file) in printable
