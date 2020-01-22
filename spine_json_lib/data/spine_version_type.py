import re
from typing import Tuple

REGEX_TO_MATCH = re.compile(r"^\d+.\d+")


class SpineVersion(object):
    def __init__(self, version):
        self.validate(version)

        self.version = version
        self.major, self.minor, self.patch = self.split_version(version)

        # Saving an integer representing the version of spine for internal comparison purposes
        # Some examples of equivalences to input format:
        # "3.6.9" <-> 3006009
        # "3.8.69" <-> 3008069
        self._int_version = self.major * 1000000 + self.minor * 1000 + self.patch

    @staticmethod
    def __force_cast_to_spine_version(obj):
        if isinstance(obj, str):
            return SpineVersion(obj)

        if not isinstance(obj, SpineVersion):
            return NotImplemented

        return obj

    def __eq__(self, other):
        """
        operator ==
        Allow check if equal to other SpineVersion or strings
        """
        _other = self.__force_cast_to_spine_version(other)

        return (
            self.major == _other.major
            and self.minor == _other.minor
            and self.patch == _other.patch
        )

    def __ne__(self, other):
        # operator !=
        return not self.__eq__(other)

    def __lt__(self, other):
        # operator <
        _other = self.__force_cast_to_spine_version(other)

        return (
            self.major < _other.major
            and self.minor < _other.minor
            and self.patch < _other.patch
        )

    def __gt__(self, other):
        # operator >
        _other = self.__force_cast_to_spine_version(other)

        return (
            self.major > _other.major
            and self.minor > _other.minor
            and self.patch > _other.patch
        )

    def __le__(self, other):
        # operator <=
        _other = self.__force_cast_to_spine_version(other)

        return (
            self.major <= _other.major
            and self.minor <= _other.minor
            and self.patch <= _other.patch
        )

    def __ge__(self, other):
        # operator >=
        _other = self.__force_cast_to_spine_version(other)

        return (
            self.major >= _other.major
            and self.minor >= _other.minor
            and self.patch >= _other.patch
        )

    def __cmp__(self, other):
        """
        This method allow us to compare SpineVersion instances with other SpineVersion
        or even with an string value.
        Some examples:
        print (SpineVersion("3.8") < "3.8.2")     # True
        print (SpineVersion("3.8.59") > "3.8.5")  # True
        print (SpineVersion("3.8.5") < "3.7")     # False
        """
        _other = self.__force_cast_to_spine_version(other)

        if self._int_version < _other._int_version:
            return -1
        elif self._int_version == _other._int_version:
            return 0
        return 1

    def __str__(self):
        return self.version

    @staticmethod
    def validate(version: str):
        has_correct_size = True

        _split_version_len = len(version.split("."))

        if not (_split_version_len == 2 or _split_version_len == 3):
            has_correct_size = False

        matched = re.match(REGEX_TO_MATCH, version)
        if not matched or not has_correct_size:
            raise ValueError(
                "{} is not a valid spine version. Needs to be "
                "of the following format 'mayor.minor.patch'".format(
                    version
                )
            )
        return True

    @staticmethod
    def split_version(version: str) -> Tuple[int, int, int]:
        """
        Take a version with the format 'major.minor.patch'
        and return a tuple of ints with (major, minor, patch).
        Will return (major, minor, 0) in case of input being 'major.minor'
        """
        SpineVersion.validate(version)
        split_version = version.split(".")
        if len(split_version) == 2:
            major, minor = split_version
            patch = 0
        else:
            major, minor, patch = split_version

        return int(major), int(minor), int(patch)
