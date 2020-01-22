import copy
from typing import Dict, Any, Optional, Callable, List, TypeVar

from spine_json_lib.data.constants import SPINE_3_8_VERSION
from spine_json_lib.data.spine_exceptions import SpineParsingException
from spine_json_lib.data.spine_version_type import SpineVersion


SpineDataType = TypeVar("SpineDataType", bound="SpineData")


class SpineData(object):
    # We want a Dict to hold information of DEFAULT_VALUES of attributes when parsing the json file
    # Attributes wont be serialized to json if they are equal to DEFAULT_VALUES[attrib_name]
    DEFAULT_VALUES: Dict[str, Any] = None

    # Will hold a list of attributes unsupported in old version
    UNSUPPORTED_VALUES_OLD_VERSION: List[str] = None

    # We want a Dict to hold information of SPINE_3_8_DEFAULT_VALUES of attributes when parsing the json file
    # Attributes wont be serialized to json if they are equal to SPINE_3_8_DEFAULT_VALUES[attrib_name]
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = None

    def __new__(cls, *args, **kwargs):
        if cls.DEFAULT_VALUES is None:
            raise NotImplementedError(
                "Missing DEFAULT_VALUES constant declaration in {} class".format(cls)
            )
        if cls.SPINE_3_8_DEFAULT_VALUES is None:
            raise NotImplementedError(
                "Missing SPINE_3_8_DEFAULT_VALUES constant declaration in {} class".format(
                    cls
                )
            )

        return super(SpineData, cls).__new__(cls)

    def __init__(self, values):
        initialized_keys = self.__dict__.keys()
        missing_attributes = []
        for k in values:
            if k not in initialized_keys:
                missing_attributes.append(k)

        if missing_attributes:
            raise SpineParsingException(
                message="Internal Error: sorry, some attributes {} are not supported in {}. "
                "Talk with product owner to add support to this spine feature".format(
                    missing_attributes, self.__class__
                )
            )

    def get(self, name, default=None):
        if hasattr(self, name) and self.__getattribute__(name) is not None:
            return self.__getattribute__(name)
        else:
            return default

    def default_values(self, version: Optional[SpineVersion] = None) -> Dict[str, Any]:
        if version is not None and version >= SPINE_3_8_VERSION:
            return copy.deepcopy(self.SPINE_3_8_DEFAULT_VALUES)
        return copy.deepcopy(self.DEFAULT_VALUES)

    def set_default_values(self, version: SpineVersion) -> None:
        # Set default values to attributes
        self.traverse_spine_data(
            obj=self, func=SpineData.set_default_values_from_version, version=version
        )

    def to_json(self, spine_version: SpineVersion) -> Dict[str, Any]:
        # Generates Json data from SpineData classes ignoring default values
        return self.traverse_spine_data(
            obj=self,
            func=SpineData.to_spine_data_ignoring_default_values,
            version=spine_version,
        )

    def clean_unsupported_attributes(self, spine_version: SpineVersion) -> None:
        # Removing unsupported attributes for an specific version of spine recursively
        self.traverse_spine_data(
            obj=self,
            func=SpineData.remove_unsupported_attributes,
            version=spine_version,
        )

    @staticmethod
    def set_default_values_from_version(obj: SpineDataType, version):
        default_values = obj.default_values(version=version)
        for k, v in obj.__dict__.items():
            if k in default_values.keys() and v is None:
                obj.__setattr__(k, default_values[k])

            if v is not None:
                obj.traverse_spine_data(
                    v, SpineData.set_default_values_from_version, version=version
                )

    @staticmethod
    def to_spine_data_ignoring_default_values(
        obj: SpineDataType, version: str
    ) -> Dict[str, Any]:
        result = {}
        default_values = obj.default_values(version=version)
        for k, v in obj.__dict__.items():
            if (
                v is None and k in default_values.keys() and default_values[k] is None
            ) or (v is not None and v != default_values.get(k)):
                result[k] = obj.traverse_spine_data(
                    v, SpineData.to_spine_data_ignoring_default_values, version=version
                )
        return result

    @staticmethod
    def remove_unsupported_attributes(obj: SpineDataType, version: str) -> None:
        for k, v in obj.__dict__.items():
            if (
                version < SPINE_3_8_VERSION
                and obj.UNSUPPORTED_VALUES_OLD_VERSION is not None
                and k in obj.UNSUPPORTED_VALUES_OLD_VERSION
            ):
                # Removing unsupported param
                obj.__setattr__(k, None)
            else:
                obj.traverse_spine_data(
                    v, SpineData.remove_unsupported_attributes, version=version
                )

    @staticmethod
    def traverse_spine_data(obj: Any, func: Callable, **kwargs: Any) -> Any:
        result: Any = None

        if isinstance(obj, (str, int, float, bool)) or obj is None:
            result = obj
        elif isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                result[k] = SpineData.traverse_spine_data(v, func, **kwargs)
        elif isinstance(obj, list):
            result = []
            for n in obj:
                result.append(SpineData.traverse_spine_data(n, func, **kwargs))
        elif issubclass(obj.__class__, SpineData):
            # In case we found an SpineData subclass keep going inside to serialize it
            result = func(obj, **kwargs)
        else:
            raise TypeError(
                "Internal error serializing spine data: {} not supported type {}".format(
                    obj, type(obj)
                )
            )

        return result
