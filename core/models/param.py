from copy import copy
import os
from tempfile import TemporaryDirectory



def check_path_valid(path, check_existence = False):
    file_exists = os.path.exists(path)
    if check_existence:
        return file_exists
 
    if file_exists:
        return True

    pathname = path.replace("/", os.path.sep)
    
    has_access = False
    pathname_copy = copy(pathname)
    while not has_access and len(pathname_copy.split(os.path.sep)) > 1:
        if os.access(pathname_copy, os.W_OK):
            has_access = True
        else:
            pathname_copy = os.path.dirname(pathname_copy)

    if not has_access:
        return False
    
    with TemporaryDirectory() as tempdir:
        rel_path = pathname.replace(pathname_copy, '')
        if rel_path.startswith("\\"):
            rel_path = rel_path[1:]
        try:
            os.makedirs(os.path.join(tempdir, rel_path))
        except Exception as e:
            print(e)
            return False
        else:
            return True


type_checker = {
    "string": str,
    "int": int,
    "float": float,
    "path": check_path_valid,
    "existingPath": check_path_valid
}


class Param:
    def __init__(self, name, description=None, type=None, default=None):
        self.name = name
        self.description = description
        self.type = type
        self.value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
        elif self.type == 'path':
            if type_checker['path'](value, check_existence=False):
                self._value = value
            else:
                raise Exception(f"Invalid path: {value}")
        elif self.type == 'existingPath':
            if type_checker['existingPath'](value, check_existence=True):
                self._value = value
            else:
                raise Exception(f"Invalid existingPath: {value}")
        else:
            if isinstance(value, type_checker[self.type]):
                self._value = value
            else:
                raise Exception(f"Invalid value: {value} {type_checker[self.type]}")

    def inject_value(self, value, copy=False):
        if copy:
            return Param(self.name, description=self.description, type=self.type, default=value)

        self.value = value
