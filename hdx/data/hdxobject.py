#!/usr/bin/python
# -*- coding: utf-8 -*-
"""HDXObject abstract class containing helper functions for creating, checking, and updating HDX objects.
New HDX objects should extend this in similar fashion to Resource for example.
"""
import abc
import copy
import logging
from collections import UserDict

import ckanapi
from ckanapi.errors import NotFound
from typing import Optional, List, Any, Tuple, TypeVar, Union

from hdx.configuration import Configuration
from hdx.utilities.dictionary import merge_two_dictionaries
from hdx.utilities.loader import load_yaml_into_existing_dict, load_json_into_existing_dict

logger = logging.getLogger(__name__)

HDXObjectUpperBound = TypeVar('T', bound='HDXObject')


class HDXError(Exception):
    pass


class HDXObject(UserDict):
    """HDXObject abstract class containing helper functions for creating, checking, and updating HDX objects.
    New HDX objects should extend this in similar fashion to Resource for example.

    Args:
        configuration (Configuration): HDX Configuration
        initial_data (dict): Initial metadata dictionary
    """
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def actions() -> dict:
        """Dictionary of actions that can be performed on object

        Returns:
            dict: dictionary of actions that can be performed on object
        """
        pass

    def __init__(self, configuration: Configuration, initial_data: dict):
        super(HDXObject, self).__init__(initial_data)
        self.configuration = configuration
        self.old_data = None
        self.hdxpostsite = ckanapi.RemoteCKAN(configuration.get_hdx_site(),
                                              apikey=configuration.get_api_key())

    def get_old_data_dict(self) -> None:
        """Get previous internal dictionary

        Returns:
            dict: Previous internal dictionary
        """
        return self.old_data

    def update_yaml(self, path: str) -> None:
        """Update metadata with static metadata from YAML file

        Args:
            path (str): Path to YAML dataset metadata

        Returns:
            None
        """
        self.data = load_yaml_into_existing_dict(self.data, path)

    def update_json(self, path: str):
        """Update metadata with static metadata from JSON file

        Args:
            path (str): Path to JSON dataset metadata

        Returns:
            None
        """
        self.data = load_json_into_existing_dict(self.data, path)

    def _read_from_hdx(self, object_type: str, id_field: str, action: Optional[str] = None) -> Tuple[bool, dict]:
        """Checks if the hdx object exists in HDX.

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field (str): HDX object identifier
            action (Optional[str]): Replacement CKAN url to use. Defaults to None.

        Returns:
            (bool, dict): (True/False, HDX object metadata/Error)
        """
        if not id_field:
            raise HDXError("Empty %s identifier!" % object_type)
        if action is None:
            action = self.actions()['show']
        try:
            result = self.hdxpostsite.call_action(action, {'id': id_field},
                                                  requests_kwargs={'auth': ('dataproject', 'humdata')})
            return True, result
        except NotFound as e:
            return False, "%s not found!" % id_field
        except Exception as e:
            raise HDXError('HTTP Get failed when trying to read %s' % id_field) from e

    def _load_from_hdx(self, object_type: str, id_field: str) -> bool:
        """Helper method to load the HDX object given by identifier from HDX

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field (str): HDX object identifier

        Returns:
            bool: True if loaded, False if not
        """
        success, result = self._read_from_hdx(object_type, id_field)
        if success:
            self.old_data = self.data
            self.data = result
            return True
        return False

    @staticmethod
    @abc.abstractmethod
    def read_from_hdx(configuration: Configuration, id_field: str) -> Optional[HDXObjectUpperBound]:
        """Abstract method to read the HDX object given by identifier from HDX and return it

        Args:
            configuration (Configuration): HDX Configuration
            id_field (str): HDX object identifier

        Returns:
            Optional[T <= HDXObject]: HDX object if successful read, None if not
        """
        return

    def _check_existing_object(self, object_type: str, id_field_name: str):
        if not self.data:
            raise HDXError("No data in %s!" % object_type)
        if id_field_name not in self.data:
            raise HDXError("No %s field (mandatory) in %s!" % (id_field_name, object_type))

    def _check_load_existing_object(self, object_type, id_field_name):
        """Check metadata exists and contains HDX object identifier, and if so load HDX object

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            None
        """
        self._check_existing_object(object_type, id_field_name)
        if not self._load_from_hdx(object_type, self.data[id_field_name]):
            raise HDXError("No existing %s to update!" % object_type)

    @abc.abstractmethod
    def check_required_fields(self, ignore_fields: List[str] = list()) -> None:
        """Abstract method to check that metadata for HDX object is complete

        Args:
            ignore_fields (List[str]): Any fields to ignore in the check. Default is empty list.

        Returns:
            None
        """
        return

    def _check_required_fields(self, object_type: str, ignore_fields: List[str]) -> None:
        """Helper method to check that metadata for HDX object is complete

        Args:
            ignore_fields (List[str]): Any fields to ignore in the check

        Returns:
            None
        """
        for field in self.configuration['%s' % object_type]['required_fields']:
            if field not in self.data and field not in ignore_fields:
                raise HDXError("Field %s is missing in %s!" % (field, object_type))

    def _merge_hdx_update(self, object_type: str, id_field_name: str) -> None:
        """Helper method to check if HDX object exists and update it

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            None
        """
        merge_two_dictionaries(self.data, self.old_data)
        self.check_required_fields(self.configuration['%s' % object_type].get('ignore_on_update', []))
        self._save_to_hdx('update', id_field_name)

    @abc.abstractmethod
    def update_in_hdx(self) -> None:
        """Abstract method to check if HDX object exists in HDX and if so, update it

        Returns:
            None
        """
        return

    def _update_in_hdx(self, object_type: str, id_field_name: str) -> None:
        """Helper method to check if HDX object exists in HDX and if so, update it

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            None
        """

        self._check_load_existing_object(object_type, id_field_name)
        self._merge_hdx_update(object_type, id_field_name)

    def _write_to_hdx(self, action: str, data: dict, id_field_name: str) -> Union[Tuple[bool, dict], Tuple[bool, str]]:
        """Creates or updates an HDX object in HDX and return HDX object metadata dict

        Args:
            action (str): Action to perform: 'create' or 'update'
            data (dict): Data to write to HDX
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            (bool, dict): (True/False, HDX object metadata/Error)
        """
        try:
            result = self.hdxpostsite.call_action(self.actions()[action], data,
                                                  requests_kwargs={'auth': ('dataproject', 'humdata')})
            return True, result
        except Exception as e:
            raise HDXError('HTTP Post failed when trying to %s %s' % (action, self.data[id_field_name])) from e

    def _save_to_hdx(self, action: str, id_field_name: str) -> None:
        """Creates or updates an HDX object in HDX, saving current data and replacing with returned HDX object data
        from HDX

        Args:
            action (str): Action to perform: 'create' or 'update'
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            None
        """
        success, result = self._write_to_hdx(action, self.data, id_field_name)

        if success:
            self.old_data = self.data
            self.data = result
        else:
            raise HDXError('Failed to %s %s\n%s' % (action, self.data[id_field_name], result))

    @abc.abstractmethod
    def create_in_hdx(self) -> None:
        """Abstract method to check if resource exists in HDX and if so, update it, otherwise create it

        Returns:
            None
        """
        return

    def _create_in_hdx(self, object_type: str, id_field_name: str, name_field_name: str) -> None:
        """Helper method to check if resource exists in HDX and if so, update it, otherwise create it


        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field_name (str): Name of field containing HDX object identifier
            name_field_name (str): Name of field containing HDX object name

        Returns:
            None
        """
        self.check_required_fields()
        if id_field_name in self.data and self._load_from_hdx(object_type, self.data[id_field_name]):
            logger.warning('%s exists. Updating %s' % (object_type, self.data[id_field_name]))
            self._merge_hdx_update(object_type, id_field_name)
        else:
            self._save_to_hdx('create', name_field_name)

    @abc.abstractmethod
    def delete_from_hdx(self) -> None:
        """Abstract method to deletes a resource from HDX

        Returns:
            None
        """
        return

    def _delete_from_hdx(self, object_type: str, id_field_name: str) -> None:
        """Helper method to deletes a resource from HDX

        Args:
            object_type (str): Description of HDX object type (for messages)
            id_field_name (str): Name of field containing HDX object identifier

        Returns:
            None
        """
        if id_field_name not in self.data:
            raise HDXError("No %s field (mandatory) in %s!" % (id_field_name, object_type))
        self._save_to_hdx('delete', id_field_name)

    @staticmethod
    def _underlying_object(_: Any, b: Any) -> Any:
        """Function to return second argument passed in

        Args:
            _ (Any): Argument to ignore
            b (Any): Argument to return

        Returns:
            Any: Return argument b
        """
        return b

    def _addupdate_hdxobject(self, hdxobjects: List[HDXObjectUpperBound], id_field: str, hdxobjectclass: type,
                             new_hdxobject: HDXObjectUpperBound) -> None:
        """Helper function to add a new HDX object to a supplied list of HDX objects or update existing metadata if the object
        already exists in the list

        Args:
            hdxobjects (list[T <= HDXObject]): List of HDX objects to which to add new objects or update existing ones
            id_field (str): Field on which to match to determine if object already exists in list
            hdxobjectclass (type): Type of the HDX Object to be added/updated
            new_hdxobject (T <= HDXObject): The HDX object to be added/updated

        Returns:
            None
        """
        found = False
        for hdxobject in hdxobjects:
            if hdxobject[id_field] == new_hdxobject[id_field]:
                merge_two_dictionaries(hdxobject, new_hdxobject)
                found = True
                break
        if not found:
            hdxobjects.append(hdxobjectclass(self.configuration, new_hdxobject))

    def _convert_hdxobjects(self, hdxobjects: List[HDXObjectUpperBound]) -> List[HDXObjectUpperBound]:
        """Helper function to convert supplied list of HDX objects to a list of dict

        Args:
            hdxobjects (list[T <= HDXObject]): List of HDX objects to convert

        Returns:
            list[dict]: List of HDX objects converted to simple dictionaries
        """
        newhdxobjects = list()
        for hdxobject in hdxobjects:
            newhdxobjects.append(hdxobject.data)
        return newhdxobjects

    def _copy_hdxobjects(self, hdxobjects: List[HDXObjectUpperBound], hdxobjectclass: type) -> List[
        HDXObjectUpperBound]:
        """Helper function to make a deep copy of a supplied list of HDX objects

        Args:
            hdxobjects (list[T <= HDXObject]): List of HDX objects to copy
            hdxobjectclass (type): Type of the HDX Objects to be copied

        Returns:
            list[T <= HDXObject]: Deep copy of list of HDX objects
        """
        newhdxobjects = list()
        for hdxobject in hdxobjects:
            newhdxobjectdata = copy.deepcopy(hdxobject.data)
            newhdxobjects.append(hdxobjectclass(self.configuration, newhdxobjectdata))
        return newhdxobjects

    def _separate_hdxobjects(self, hdxobjects: List[HDXObjectUpperBound], hdxobjects_name: str, id_field: str,
                             hdxobjectclass: type) -> None:
        """Helper function to take a list of HDX objects contained in the internal dictionary and add them to a
        supplied list of HDX objects or update existing metadata if any objects already exist in the list. The list in
        the internal dictionary is then deleted.

        Args:
            hdxobjects (list[T <= HDXObject]): List of HDX objects to which to add new objects or update existing ones
            hdxobjects_name (str): Name of key in internal dictionary from which to obtain list of HDX objects
            id_field (str): Field on which to match to determine if object already exists in list
            hdxobjectclass (type): Type of the HDX Object to be added/updated

        Returns:
            None
        """
        new_hdxobjects = self.data.get(hdxobjects_name, None)
        if new_hdxobjects:
            hdxobject_names = set()
            for hdxobject in hdxobjects:
                hdxobject_name = hdxobject[id_field]
                hdxobject_names.add(hdxobject_name)
                for new_hdxobject in new_hdxobjects:
                    if hdxobject_name == new_hdxobject[id_field]:
                        merge_two_dictionaries(hdxobject, new_hdxobject)
                        break
            for new_hdxobject in new_hdxobjects:
                if not new_hdxobject[id_field] in hdxobject_names:
                    hdxobjects.append(hdxobjectclass(self.configuration, new_hdxobject))
            del self.data[hdxobjects_name]
