# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021 The Anvil Extras project team members listed at
# https://github.com/anvilistas/anvil-extras/graphs/contributors
#
# This software is published at https://github.com/anvilistas/anvil-extras

import pathlib
from datetime import date, datetime

from pydal import DAL, Field

import anvil.js
from anvil.js import ExternalError
from anvil.js import window as _window
from anvil.users import pytest_identifier

__version__ = "2.5.4"
__all__ = ["local_storage", "indexed_db"]

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# FOR TESTING
from typing import Iterable

abs_path = pathlib.Path(__file__).parent.parent.parent / 'tests_project'
if not abs_path.exists():
    abs_path.mkdir()
abs_path = abs_path / 'databases'
if not abs_path.exists():
    abs_path.mkdir()


class _Forage:
    """A wrapper for the forage.js library. It is a singleton class."""
    INDEXEDDB = "indexeddb"
    LOCALSTORAGE = "localstorage"
    database_name = "browser_indexedDB"  # + str(datetime.utcnow())
    _db = DAL('sqlite://{}.sqlite'.format(database_name), folder=abs_path)

    def __init__(self, name):
        self._name = name

    def dropInstance(self):
        if self._name in _Forage._db.tables:
            _Forage._db[self._name].drop()
            _Forage._db.commit()

    @classmethod
    def createInstance(cls, init_options):
        store_name = init_options["storeName"]
        if store_name not in cls._db.tables:
            cls._db.define_table(store_name,
                                 Field('key', type='string', default=None),
                                 Field('value', type='json', default=None),
                                 Field('current_test', type='string', default=None))
            cls._db.commit()
        return _Forage(store_name)

    def defineDriver(self, driver):
        # do not need any error handling here
        pass

    @property
    def _db_pytest_query(self):
        return _Forage._db[self._name].current_test == pytest_identifier()

    def _db_query(self, key):
        return (_Forage._db[self._name].key == key) & self._db_pytest_query

    def getItem(self, key) -> dict:
        """get an item from the store"""
        return _Forage._db(self._db_query(key)).select().first()['value']

    def setItem(self, key, val):
        """set an item in the store"""
        # delete item
        self.removeItem(key)
        # insert item
        _Forage._db[self._name].insert(key=key, value=val, current_test=pytest_identifier())
        _Forage._db.commit()

    def removeItem(self, key):
        """remove an item from the store"""
        _Forage._db(self._db_query(key)).delete()
        _Forage._db.commit()

    def keys(self) -> Iterable:
        """get all keys in the store"""
        return (row.key for row in _Forage._db(self._db_pytest_query).select(_Forage._db[self._name].key))

    def length(self) -> int:
        """get the number of items in the store"""
        return _Forage._db(self._db_pytest_query).count()

    @staticmethod
    def supports(feature) -> bool:
        """check if the store supports a feature"""
        if feature:
            return True
        return False

    def clear(self):
        """clear the store"""
        _Forage._db(self._db_pytest_query).delete()
        _Forage._db.commit()


class _ForageModule(_Forage):
    default = _Forage("default")


_window.localforage = _ForageModule.default
# END FOR TESTING
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

try:
    _forage = _window.localforage
except AttributeError:
    _ForageModule = anvil.js.import_from(
        "https://cdn.skypack.dev/pin/localforage@v1.10.0-vSTz1U7CF0tUryZh6xTs/mode=imports,min/optimized/localforage.js"
    )
    _forage = _ForageModule.default

_forage.dropInstance()


_Proxy = type(_window)
_Object = _window.Object
_NoneType = type(None)
_Array = type(_window.Array())

_SPECIAL = "$$anvil-extras$$:"


def _is_str(key):
    if type(key) is not str:
        msg = f"Keys must be strings when serialzing to browser Storage. Found {type(key).__name__}"
        raise TypeError(msg)
    return True


def _serialize(obj):
    # we won't support subclasses of builtins so just check type is
    ob_type = type(obj)
    if ob_type in (str, int, float, bool, _NoneType, bytes):
        return obj
    elif ob_type in (list, tuple, _Array):
        return [_serialize(item) for item in obj]
    elif ob_type is dict:
        return {key: _serialize(val) for key, val in obj.items() if _is_str(key)}
    elif ob_type is datetime:
        return {_SPECIAL + "datetime": obj.isoformat()}
    elif ob_type is date:
        return {_SPECIAL + "date": obj.isoformat()}
    else:
        raise TypeError(f"Cannot serialize an object of type {ob_type.__name__}")


_deserializers = {"date": date.fromisoformat, "datetime": datetime.fromisoformat}


def _special_deserialize(key, value):
    assert key.startswith(_SPECIAL), "not a special key"
    key = key[len(_SPECIAL) :]
    try:
        return _deserializers[key](value)
    except KeyError:
        raise ValueError(f"unknown special deserialization type {key!r}")


def _deserialize(obj):
    """convert simple proxy objects (and nested simple proxy objects) to dictionaries"""
    ob_type = type(obj)
    if ob_type in (list, _Array):
        return [_deserialize(item) for item in obj]
    # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    # FOR TESTING
    simple = False
    keys = []
    try:
        keys = [_ for _ in obj.keys()]
    except AttributeError:
        # not a object
        simple = True
    if not simple:
        # elif ob_type is _Proxy and obj.__class__ == _Object:
        #     # Then we're a simple proxy object
        #     # keys are strings so only _deserialize the values
        #     # use _Object.keys to avoid possible name conflict
        #     keys = _Object.keys(obj)
        # END FOR TESTING
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        if len(keys) == 1 and keys[0].startswith(_SPECIAL):
            key = keys[0]
            return _special_deserialize(key, obj[key])
        return {key: _deserialize(obj[key]) for key in keys}
    else:
        # we're either bytes, str, ints, floats, None, bool
        return obj


def wrap_with_retry(fn):
    def wrapper(*args, **kws):
        try:
            return fn(*args, **kws)
        except ExternalError:
            try:
                return fn(*args, **kws)
            except ExternalError:
                raise

    return wrapper


class RetryStoreWrapper:
    def __init__(self, store):
        self._store = store

    def __getattr__(self, name):
        maybe_method = getattr(self._store, name)
        if callable(maybe_method):
            return wrap_with_retry(maybe_method)
        return maybe_method


class StorageWrapper:
    _driver = None
    _stores = None

    def __new__(cls, store_name):
        if cls._driver is None:
            raise NotImplementedError(
                "StorageWrapper cannot be initiated without a valid _driver"
            )
        if not isinstance(store_name, str):
            raise TypeError(
                f"store_name should be a str, (got {store_name.__class__.__name__})"
            )
        known_stores = cls._stores
        if known_stores is None:
            # initialize the _stores cache
            known_stores = cls._stores = {}
        elif store_name in known_stores:
            return known_stores[store_name]

        store = object.__new__(cls)
        forage_store = _forage.createInstance(
            {
                "storeName": store_name,
                "driver": [cls._driver, f"fail{cls._driver}"],
                "name": "anvil_extras",
            }
        )
        store._store = RetryStoreWrapper(forage_store)
        store._name = store_name
        known_stores[store_name] = store
        return store

    def is_available(self):
        """check if the store object is available and accessible."""
        # in some browsers localStorageWrapper might not be available
        if not self._store.supports(self._driver):
            # we cn't rely on this method - it's just for browser support
            return False
        # noinspection PyBroadException
        try:
            self._store.length()
            # call a method in the store to activate the store
            return True
        except Exception:
            return False

    def __getitem__(self, key):
        if key in self._store.keys():
            return _deserialize(self._store.getItem(key))
        raise KeyError(key)

    def __setitem__(self, key, val):
        self._store.setItem(key, _serialize(val))

    def __delitem__(self, key):
        # we can't block here so do a Promise hack
        _window.Promise(lambda res, rej: self._store.removeItem(key))
        return None

    def __contains__(self, key):
        return key in self._store.keys()

    def __repr__(self):
        # we can't print the items like a dictionary since we get a SuspensionError here
        return f"<{self.__class__.__name__} for {self._name!r} store>"

    def __iter__(self):
        # self.keys() suspends and __iter__ can't suspend
        return StoreIterator(self)

    def __len__(self):
        return self._store.length()

    def keys(self):
        """returns the keys for the store as an iterator"""
        return self._store.keys()

    def items(self):
        """returns the items for the store as an iterator"""
        return (
            (key, _deserialize(self._store.getItem(key))) for key in self._store.keys()
        )

    def values(self):
        """returns the values for the store as an iterator"""
        return (_deserialize(self._store.getItem(key)) for key in self._store.keys())

    def store(self, key: str, value):
        """store a key value pair in the store"""
        self[key] = value

    put = store  # backward compatibility

    def get(self, key: str, default=None):
        """get a value from the store, returns the default value if the key is not in the store"""
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: str, default=None):
        """remove specified key and return the corresponding value.\n\nIf key is not found, default is returned"""
        try:
            return self.get(key, default)
        finally:
            del self[key]

    def clear(self):
        """clear all items from the store"""
        self._store.clear()

    def update(self, other, **kws):
        """update the store item with key/value pairs from other"""
        other = dict(other, **kws)
        for key, value in other.items():
            self[key] = value

    @classmethod
    def create_store(cls, store_name: str):
        """
        Create a new storage object inside the browser's IndexedDB or localStorage.
        e.g. todo_store = indexed_db.create_store('todos')
        message_store = indexed_db.create_store('messages')
        """
        return cls(store_name)


class StoreIterator:
    def __init__(self, store):
        self._store = store
        self._keys = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._keys is None:
            self._keys = iter(self._store.keys())
        return next(self._keys)


# The following defines a forage driver whose job is to
# try to access the appropriate browser store,
# catch the exception and the throw a nicer exception
def _fail_access(fn):
    def _do_fail(*args):
        # see what happens when we try to access the storage object
        msg = "Browser storage object is not available."
        try:
            fn()
        except Exception as e:
            msg += f"\nWhen trying to access the storage object got - {e}"
        raise RuntimeError(msg)

    return _do_fail


def _fail_db(*args):
    def check_db(res, rej):
        req = _window.indexedDB.open("anvil_extras")
        req.onerror = lambda e: rej(req.error.toString())
        req.onsuccess = lambda r: res(None)

    # this is asyncronous so use the Promise api
    anvil.js.await_promise(_window.Promise(check_db))


def _fail_ls(*args):
    _window.get("localStorage")


def _defineFailDriver(driver: str):
    fail_fn = _fail_db if driver == _forage.INDEXEDDB else _fail_ls
    fail_callback = _fail_access(fail_fn)
    _forage.defineDriver(
        {
            "_driver": f"fail{driver}",
            "_initStorage": lambda options: None,
            "clear": fail_callback,
            "getItem": fail_callback,
            "iterate": fail_callback,
            "key": fail_callback,
            "keys": fail_callback,
            "length": fail_callback,
            "removeItem": fail_callback,
            "setItem": fail_callback,
        }
    )


_defineFailDriver(_forage.INDEXEDDB)
_defineFailDriver(_forage.LOCALSTORAGE)


class IndexedDBWrapper(StorageWrapper):
    _driver = _forage.INDEXEDDB


indexed_db = IndexedDBWrapper.create_store("default")


class LocalStorageWrapper(StorageWrapper):
    _driver = _forage.LOCALSTORAGE


local_storage = LocalStorageWrapper.create_store("default")


def __getattr__(name):
    if name == "session_storage":
        raise Exception("deprecated - session_storage is no longer supported")
    raise AttributeError(name)


if __name__ == "__main__":
    for _ in local_storage, indexed_db:
        print(_)
        _["foo"] = "bar"
        assert _["foo"] == "bar"
        del _["foo"]
        assert _.get("foo", "sentinel") == "sentinel"
        try:
            _["foo"]
        except KeyError:
            pass
        else:
            raise AssertionError
        _.put("foo", 1)
        assert _.pop("foo") == 1
        x = [{"a": "b"}, "foo"]
        _["x"] = x
        assert _["x"] == x == _.get("x") == _.pop("x")
        _["foo"] = None
        _["eggs"] = None
        _.update({"foo": "bar"}, eggs="spam", x=1)
        for i in _:  # shouldn't fail
            pass
        assert len(list(_.keys())) == 3 and _["eggs"] == "spam"
        assert list(_) == list(_.keys())

        date_objs = [datetime.now(), datetime.now().astimezone(), date.today()]
        _["d"] = date_objs
        assert _["d"] == date_objs
        try:
            _["foo"] = slice(1, 2, 3)
        except TypeError:
            pass
        else:
            raise AssertionError

        _.clear()
        assert len(_) == 0
        print("===== Tests Passed =====")
