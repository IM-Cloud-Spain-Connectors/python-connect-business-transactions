#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from typing import List, Optional, Tuple

from connect.eaas.core.responses import BackgroundResponse
from rndi.connect_business_transactions.exceptions import TransactionException
from rndi.connect_business_transactions.contracts import (
    AnyBackgroundTransaction,
    BackgroundTransaction,
    FnBackgroundCompensation,
    FnBackgroundExecution,
    FnBackgroundPredicate,
    TBackgroundResponse,
)


class TupleBackgroundTransaction(BackgroundTransaction):
    def __init__(
            self,
            name: str,
            predicate: FnBackgroundPredicate,
            execution: FnBackgroundExecution,
            compensation: Optional[FnBackgroundCompensation] = None,
    ):
        self._name = name
        self._predicate = predicate
        self._execution = execution
        self._compensation = compensation

    def name(self) -> str:
        return self._name

    def should_execute(self, request: dict) -> bool:
        return self._predicate(request)

    def execute(self, request: dict) -> BackgroundResponse:
        return self._execution(request)

    def compensate(self, request: dict, e: Exception) -> BackgroundResponse:
        if self._compensation is None:
            raise e
        return self._compensation(request, e)


def select(transactions: List[AnyBackgroundTransaction], request: dict) -> BackgroundTransaction:
    """
    Select the correct transaction for the given request (context).

    :param transactions: List[AnyBackgroundTransactionStatement] List of transactions.
    :param request: dict The Connect Request dictionary.
    :return: BackgroundTransaction
    """

    def __prepare_transaction_statement(any_statement: AnyBackgroundTransaction) -> BackgroundTransaction:
        if isinstance(any_statement, BackgroundTransaction):
            return any_statement
        elif isinstance(any_statement, Tuple):
            print(any_statement)
            return TupleBackgroundTransaction(*any_statement)
        else:
            raise TransactionException.invalid('Invalid transaction.')

    for transaction in [__prepare_transaction_statement(t) for t in transactions if t]:
        if transaction.should_execute(request):
            return transaction
    raise TransactionException.not_selected('Unable to select a transaction.')


def prepare(transaction: BackgroundTransaction) -> FnBackgroundExecution:
    def __transaction_executor(request: dict) -> TBackgroundResponse:
        try:
            return transaction.execute(request)
        except Exception as e:
            return transaction.compensate(request, e)

    return __transaction_executor


class TransactionSelector:
    def __init__(self, transactions: List[AnyBackgroundTransaction]):
        self.__transactions = transactions

    def select(self, request: dict) -> FnBackgroundExecution:
        return prepare(select(self.__transactions, request))
