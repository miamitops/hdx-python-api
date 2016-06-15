#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Resource Tests"""
import copy
import json
from os.path import join

import pytest
import requests

from hdx.configuration import Configuration
from hdx.data.hdxobject import HDXError
from hdx.data.resource import Resource
from hdx.utilities.dictionary import merge_two_dictionaries


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def json(self):
        return json.loads(self.text)


class TestResource():
    resource_data = {
        'name': 'MyResource1',
        'package_id': '6f36a41c-f126-4b18-aaaf-6c2ddfbc5d4d',
        'format': 'xlsx',
        'url': 'http://test/spreadsheet.xlsx',
        'description': 'My Resource'
    }

    resultdict = {'cache_last_updated': None, 'package_id': '6f36a41c-f126-4b18-aaaf-6c2ddfbc5d4d',
                  'webstore_last_updated': None, 'datastore_active': None,
                  'id': 'de6549d8-268b-4dfe-adaf-a4ae5c8510d5', 'size': None, 'state': 'active',
                  'hash': '', 'description': 'My Resource', 'format': 'XLSX',
                  'tracking_summary': {'total': 0, 'recent': 0}, 'last_modified': None, 'url_type': None,
                  'mimetype': None, 'cache_url': None, 'name': 'MyResource1',
                  'created': '2016-06-07T08:57:27.367939', 'url': 'http://test/spreadsheet.xlsx',
                  'webstore_url': None, 'mimetype_inner': None, 'position': 0,
                  'revision_id': '43765383-1fce-471f-8166-d6c8660cc8a9', 'resource_type': None}

    @pytest.fixture(scope='class')
    def static_yaml(self):
        return join('fixtures', 'config', 'hdx_resource_static.yml')

    @pytest.fixture(scope='class')
    def static_json(self):
        return join('fixtures', 'config', 'hdx_resource_static.json')

    @pytest.fixture(scope='function')
    def get(self, monkeypatch):
        def mockreturn(url, headers, auth):
            result = json.dumps(TestResource.resultdict)
            if 'TEST1' in url:
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_show"}' % result)
            if 'TEST2' in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_show"}')
            if 'TEST3' in url:
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_show"}' % result)
            if 'TEST4' in url:
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_show"}')
            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_show"}')

        monkeypatch.setattr(requests, 'get', mockreturn)

    @pytest.fixture(scope='function')
    def post_create(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'create' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not create", "__type": "TEST ERROR: Not Create Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}')
            datadict = json.loads(data)

            result = json.dumps(TestResource.resultdict)
            if datadict['name'] == 'MyResource1':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}' % result)
            if datadict['name'] == 'MyResource2':
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}')
            if datadict['name'] == 'MyResource3':
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}' % result)
            if datadict['name'] == 'MyResource4':
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}')

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_create"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='function')
    def post_update(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'update' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not update", "__type": "TEST ERROR: Not Update Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}')
            datadict = json.loads(data)
            resultdict = copy.deepcopy(TestResource.resultdict)
            merge_two_dictionaries(resultdict, datadict)

            result = json.dumps(resultdict)
            if datadict['name'] == 'MyResource1':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}' % result)
            if datadict['name'] == 'MyResource2':
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}')
            if datadict['name'] == 'MyResource3':
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}' % result)
            if datadict['name'] == 'MyResource4':
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}')

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_update"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='function')
    def post_delete(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'delete' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not delete", "__type": "TEST ERROR: Not Delete Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_delete"}')
            datadict = json.loads(data)
            if datadict['id'] == 'de6549d8-268b-4dfe-adaf-a4ae5c8510d5':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_delete"}' % data)

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=resource_delete"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='class')
    def configuration(self):
        hdx_key_file = join('fixtures', '.hdxkey')
        collector_config_yaml = join('fixtures', 'config', 'collector_configuration.yml')
        return Configuration(hdx_key_file=hdx_key_file, collector_config_yaml=collector_config_yaml)

    def test_read_from_hdx(self, configuration, get):
        resource = Resource.read_from_hdx(configuration, 'TEST1')
        assert resource['id'] == 'de6549d8-268b-4dfe-adaf-a4ae5c8510d5'
        assert resource['name'] == 'MyResource1'
        assert resource['package_id'] == '6f36a41c-f126-4b18-aaaf-6c2ddfbc5d4d'
        resource = Resource.read_from_hdx(configuration, 'TEST2')
        assert resource is None
        with pytest.raises(HDXError):
            resource = Resource.read_from_hdx(configuration, 'TEST3')
        resource = Resource.read_from_hdx(configuration, 'TEST4')
        assert resource is None

    def test_create_in_hdx(self, configuration, get, post_create):
        resource = Resource(configuration)
        with pytest.raises(HDXError):
            resource.create_in_hdx()
        resource['id'] = 'TEST1'
        resource['name'] = 'LALA'
        with pytest.raises(HDXError):
            resource.create_in_hdx()

        resource_data = copy.deepcopy(TestResource.resource_data)
        resource = Resource(configuration, resource_data)
        resource.create_in_hdx()
        assert resource['id'] == 'de6549d8-268b-4dfe-adaf-a4ae5c8510d5'

        resource_data['name'] = 'MyResource2'
        resource = Resource(configuration, resource_data)
        with pytest.raises(HDXError):
            resource.create_in_hdx()

        resource['name'] = 'MyResource3'
        with pytest.raises(HDXError):
            resource.create_in_hdx()

        resource_data['name'] = 'MyResource4'
        resource = Resource(configuration, resource_data)
        with pytest.raises(HDXError):
            resource.create_in_hdx()

    def test_update_in_hdx(self, configuration, get, post_update):
        resource = Resource(configuration)
        resource['id'] = 'NOTEXIST'
        with pytest.raises(HDXError):
            resource.update_in_hdx()
        resource['name'] = 'LALA'
        with pytest.raises(HDXError):
            resource.update_in_hdx()

        resource = Resource.read_from_hdx(configuration, 'TEST1')
        assert resource['id'] == 'de6549d8-268b-4dfe-adaf-a4ae5c8510d5'
        assert resource['format'] == 'XLSX'

        resource['format'] = 'CSV'
        resource['id'] = 'TEST1'
        resource['name'] = 'MyResource1'
        resource.update_in_hdx()
        assert resource['id'] == 'TEST1'
        assert resource['format'] == 'CSV'

        resource['id'] = 'NOTEXIST'
        with pytest.raises(HDXError):
            resource.update_in_hdx()

        del resource['id']
        with pytest.raises(HDXError):
            resource.update_in_hdx()

        resource_data = copy.deepcopy(TestResource.resource_data)
        resource_data['name'] = 'MyResource1'
        resource_data['id'] = 'TEST1'
        resource = Resource(configuration, resource_data)
        resource.create_in_hdx()
        assert resource['id'] == 'TEST1'
        assert resource['format'] == 'xlsx'

    def test_delete_from_hdx(self, configuration, get, post_delete):
        resource = Resource.read_from_hdx(configuration, 'TEST1')
        resource.delete_from_hdx()
        del resource['id']
        with pytest.raises(HDXError):
            resource.delete_from_hdx()

    def test_update_yaml(self, configuration, static_yaml):
        resource_data = copy.deepcopy(TestResource.resource_data)
        resource = Resource(configuration, resource_data)
        assert resource['name'] == 'MyResource1'
        assert resource['format'] == 'xlsx'
        resource.update_yaml(static_yaml)
        assert resource['name'] == 'MyResource1'
        assert resource['format'] == 'csv'

    def test_update_json(self, configuration, static_json):
        resource_data = copy.deepcopy(TestResource.resource_data)
        resource = Resource(configuration, resource_data)
        assert resource['name'] == 'MyResource1'
        assert resource['format'] == 'xlsx'
        resource.update_yaml(static_json)
        assert resource['name'] == 'MyResource1'
        assert resource['format'] == 'zipped csv'