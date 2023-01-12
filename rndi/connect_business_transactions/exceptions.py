#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations


class TransactionException(Exception):
    @staticmethod
    def invalid(msg: str) -> InvalidTransaction:
        return InvalidTransaction(msg)

    @staticmethod
    def not_selected(msg: str) -> TransactionNotSelected:
        return TransactionNotSelected(msg)


class InvalidTransaction(TransactionException):
    pass


class TransactionNotSelected(TransactionException):
    pass
