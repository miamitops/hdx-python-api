#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""GalleryItem Tests"""
import copy
import json
from os.path import join

import pytest
import requests

from hdx.configuration import Configuration
from hdx.data.galleryitem import GalleryItem
from hdx.data.hdxobject import HDXError
from hdx.utilities.dictionary import merge_two_dictionaries


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def json(self):
        return json.loads(self.text)


class TestGalleryItem():
    galleryitem_data = {
        'title': 'MyGalleryItem1',
        'description': 'My GalleryItem',
        'dataset_id': '6f36a41c-f126-4b18-aaaf-6c2ddfbc5d4d',
        'image_url': 'http://myvisual/visual.png',
        'type': 'visualization',
        'url': 'http://visualisation/url/'
    }

    resultdict = {
        'description': 'My GalleryItem',
        '__extras': {
            'view_count': 1
        },
        'url': 'http://visualisation/url/',
        'title': 'MyGalleryItem1',
        'featured': 0,
        'image_url': 'http://myvisual/visual.png',
        'type': 'visualization',
        'id': '2f90d964-f980-4513-ad1b-5df6b2d044ff',
        'owner_id': '196196be-6037-4488-8b71-d786adf4c081'
    }

    @pytest.fixture(scope='function')
    def get(self, monkeypatch):
        def mockreturn(url, headers, auth):
            result = json.dumps(TestGalleryItem.resultdict)
            if 'TEST1' in url:
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_show"}' % result)
            if 'TEST2' in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_show"}')
            if 'TEST3' in url:
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_show"}' % result)
            if 'TEST4' in url:
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_show"}')
            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_show"}')

        monkeypatch.setattr(requests, 'get', mockreturn)

    @pytest.fixture(scope='function')
    def post_create(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'create' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not create", "__type": "TEST ERROR: Not Create Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}')
            datadict = json.loads(data)

            result = json.dumps(TestGalleryItem.resultdict)
            if datadict['title'] == 'MyGalleryItem1':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}' % result)
            if datadict['title'] == 'MyGalleryItem2':
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}')
            if datadict['title'] == 'MyGalleryItem3':
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}' % result)
            if datadict['title'] == 'MyGalleryItem4':
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}')

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_create"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='function')
    def post_update(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'update' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not update", "__type": "TEST ERROR: Not Update Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}')
            datadict = json.loads(data)
            resultdict = copy.deepcopy(TestGalleryItem.resultdict)
            merge_two_dictionaries(resultdict, datadict)

            result = json.dumps(resultdict)
            if datadict['title'] == 'MyGalleryItem1':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}' % result)
            if datadict['title'] == 'MyGalleryItem2':
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}')
            if datadict['title'] == 'MyGalleryItem3':
                return MockResponse(404,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}' % result)
            if datadict['title'] == 'MyGalleryItem4':
                return MockResponse(200,
                                    '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}')

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_update"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='function')
    def post_delete(self, monkeypatch):
        def mockreturn(url, data, headers, auth):
            if 'delete' not in url:
                return MockResponse(404,
                                    '{"success": false, "error": {"message": "TEST ERROR: Not delete", "__type": "TEST ERROR: Not Delete Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_delete"}')
            datadict = json.loads(data)
            if datadict['id'] == '2f90d964-f980-4513-ad1b-5df6b2d044ff':
                return MockResponse(200,
                                    '{"success": true, "result": %s, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_delete"}' % data)

            return MockResponse(404,
                                '{"success": false, "error": {"message": "Not found", "__type": "Not Found Error"}, "help": "http://test-data.humdata.org/api/3/action/help_show?name=related_delete"}')

        monkeypatch.setattr(requests, 'post', mockreturn)

    @pytest.fixture(scope='class')
    def configuration(self):
        hdx_key_file = join('fixtures', '.hdxkey')
        collector_config_yaml = join('fixtures', 'config', 'collector_configuration.yml')
        return Configuration(hdx_key_file=hdx_key_file, collector_config_yaml=collector_config_yaml)

    def test_read_from_hdx(self, configuration, get):
        galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST1')
        assert galleryitem['id'] == '2f90d964-f980-4513-ad1b-5df6b2d044ff'
        assert galleryitem['title'] == 'MyGalleryItem1'
        galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST2')
        assert galleryitem is None
        with pytest.raises(HDXError):
            galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST3')
        galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST4')
        assert galleryitem is None

    def test_create_in_hdx(self, configuration, get, post_create):
        galleryitem = GalleryItem(configuration)
        with pytest.raises(HDXError):
            galleryitem.create_in_hdx()
        galleryitem['id'] = 'TEST1'
        galleryitem['title'] = 'LALA'
        with pytest.raises(HDXError):
            galleryitem.create_in_hdx()

        galleryitem_data = copy.deepcopy(TestGalleryItem.galleryitem_data)
        galleryitem = GalleryItem(configuration, galleryitem_data)
        galleryitem.create_in_hdx()
        assert galleryitem['id'] == '2f90d964-f980-4513-ad1b-5df6b2d044ff'

        galleryitem_data['title'] = 'MyGalleryItem2'
        galleryitem = GalleryItem(configuration, galleryitem_data)
        with pytest.raises(HDXError):
            galleryitem.create_in_hdx()

        galleryitem['title'] = 'MyGalleryItem3'
        with pytest.raises(HDXError):
            galleryitem.create_in_hdx()

        galleryitem_data['title'] = 'MyGalleryItem4'
        galleryitem = GalleryItem(configuration, galleryitem_data)
        with pytest.raises(HDXError):
            galleryitem.create_in_hdx()

    def test_update_in_hdx(self, configuration, get, post_update):
        galleryitem = GalleryItem(configuration)
        galleryitem['id'] = 'NOTEXIST'
        with pytest.raises(HDXError):
            galleryitem.update_in_hdx()
        galleryitem['title'] = 'LALA'
        with pytest.raises(HDXError):
            galleryitem.update_in_hdx()

        galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST1')
        assert galleryitem['id'] == '2f90d964-f980-4513-ad1b-5df6b2d044ff'
        assert galleryitem['type'] == 'visualization'

        galleryitem['type'] = 'paper'
        galleryitem['id'] = 'TEST1'
        galleryitem['title'] = 'MyGalleryItem1'
        galleryitem.update_in_hdx()
        assert galleryitem['id'] == 'TEST1'
        assert galleryitem['type'] == 'paper'

        galleryitem['id'] = 'NOTEXIST'
        with pytest.raises(HDXError):
            galleryitem.update_in_hdx()

        del galleryitem['id']
        with pytest.raises(HDXError):
            galleryitem.update_in_hdx()

        galleryitem_data = copy.deepcopy(TestGalleryItem.galleryitem_data)
        galleryitem_data['title'] = 'MyGalleryItem1'
        galleryitem_data['id'] = 'TEST1'
        galleryitem = GalleryItem(configuration, galleryitem_data)
        galleryitem.create_in_hdx()
        assert galleryitem['id'] == 'TEST1'
        assert galleryitem['type'] == 'visualization'

    def test_delete_from_hdx(self, configuration, get, post_delete):
        galleryitem = GalleryItem.read_from_hdx(configuration, 'TEST1')
        galleryitem.delete_from_hdx()
        del galleryitem['id']
        with pytest.raises(HDXError):
            galleryitem.delete_from_hdx()
