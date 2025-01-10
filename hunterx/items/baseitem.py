# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/6 16:15
# @Version: 1.0.0
# @Description: 'hunterx Item'
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    def __setattr__(self, name: str, value: Any) -> None:
        # 允许直接设置实例的属性
        if name in self.__dataclass_fields__:
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

    def to_dict(self) -> dict[str, Any]:
        """
        将 dataclass 实例转换为字典
        """
        return {field.name: getattr(self, field.name) for field in self.__dataclass_fields__.values()}

# from __future__ import annotations
# from time import time
# from collections import defaultdict
# from weakref import WeakKeyDictionary
#
# from abc import ABCMeta
# from collections.abc import MutableMapping
# from copy import deepcopy
# from pprint import pformat
# from typing import TYPE_CHECKING, Any, NoReturn
#
# live_refs: defaultdict[type, WeakKeyDictionary] = defaultdict(WeakKeyDictionary)
#
#
# class object_ref:
#     __slots__ = ()
#
#     def __new__(cls, *args: Any, **kwargs: Any) -> Self:
#         obj = object.__new__(cls)
#         live_refs[cls][obj] = time()
#         return obj
#
#
# if TYPE_CHECKING:
#     from collections.abc import Iterator, KeysView
#
#     # typing.Self requires Python 3.11
#     from typing_extensions import Self
#
#
# class Field:
#     """描述符，用于支持属性赋值功能"""
#
#     def __init__(self, default=None):
#         self.default = default
#
#     def __get__(self, instance: Item, owner: type[Item]) -> Any:
#         """获取属性值"""
#         if instance is None:
#             return self
#         return instance._values.get(self, self.default)
#
#     def __set__(self, instance: Item, value: Any) -> None:
#         """设置属性值"""
#         instance._values[self] = value
#
#     def __delete__(self, instance: Item) -> None:
#         """删除属性值"""
#         del instance._values[self]
#
#
# class ItemMeta(ABCMeta):
#     """Metaclass_ of :class:`Item` that handles field definitions.
#
#     .. _metaclass: https://realpython.com/python-metaclasses
#     """
#
#     def __new__(
#             mcs, class_name: str, bases: tuple[type, ...], attrs: dict[str, Any]
#     ) -> ItemMeta:
#         classcell = attrs.pop("__classcell__", None)
#         new_bases = tuple(base._class for base in bases if hasattr(base, "_class"))
#         _class = super().__new__(mcs, "x_" + class_name, new_bases, attrs)
#
#         fields = getattr(_class, "fields", {})
#         new_attrs = {}
#         for n in dir(_class):
#             v = getattr(_class, n)
#             if isinstance(v, Field):
#                 fields[n] = v
#             elif n in attrs:
#                 new_attrs[n] = attrs[n]
#
#         new_attrs["fields"] = fields
#         new_attrs["_class"] = _class
#         if classcell is not None:
#             new_attrs["__classcell__"] = classcell
#         return super().__new__(mcs, class_name, bases, new_attrs)
#
#
# class Item(MutableMapping[str, Any], object_ref, metaclass=ItemMeta):
#     fields: dict[str, Field]
#
#     def __init__(self, *args: Any, **kwargs: Any):
#         self._values: dict[str, Any] = {}
#         if args or kwargs:  # avoid creating dict for most common case
#             for k, v in dict(*args, **kwargs).items():
#                 self[k] = v
#
#     def __getitem__(self, key: str) -> Any:
#         return self._values[key]
#
#     def __setitem__(self, key: str, value: Any) -> None:
#         if key in self.fields:
#             self._values[key] = value
#         else:
#             raise KeyError(f"{self.__class__.__name__} does not support field: {key}")
#
#     def __delitem__(self, key: str) -> None:
#         del self._values[key]
#
#     def __getattr__(self, name: str) -> NoReturn:
#         if name in self.fields:
#             raise AttributeError(f"Use item[{name!r}] to get field value")
#         raise AttributeError(name)
#
#     def __setattr__(self, name: str, value: Any) -> None:
#         if name in self.fields:
#             self._values[name] = value
#         else:
#             super().__setattr__(name, value)
#
#     def __len__(self) -> int:
#         return len(self._values)
#
#     def __iter__(self) -> Iterator[str]:
#         return iter(self._values)
#
#     __hash__ = object_ref.__hash__
#
#     def keys(self) -> KeysView[str]:
#         return self._values.keys()
#
#     def __repr__(self) -> str:
#         return pformat(dict(self))
#
#     def copy(self) -> Self:
#         return self.__class__(self)
#
#     def deepcopy(self) -> Self:
#         """Return a :func:`~copy.deepcopy` of this item."""
#         return deepcopy(self)
#
#     def to_dict(self, include_fields: bool = True) -> dict[str, Any]:
#         """
#         将 Item 实例的字段和值转换为字典形式返回。
#
#         :param include_fields: 是否包含所有字段，默认为 True
#         :return: 字典格式的字段和值
#         """
#         if include_fields:
#             return dict(self._values)
#         return {k: v for k, v in self._values.items() if k in self.fields}
