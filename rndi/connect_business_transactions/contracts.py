#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from abc import ABC, abstractmethod
from typing import Callable, Tuple, TypeVar, Union

from connect.eaas.core.responses import (
    BackgroundResponse,
    InteractiveResponse,
    ScheduledExecutionResponse,
    ValidationResponse,
)

TBackgroundResponse = TypeVar('TBackgroundResponse', bound=BackgroundResponse)


class BackgroundTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def name(self) -> str:
        """
        Provides the transaction name.

        :return: str
        """

    @abstractmethod
    def should_execute(self, request: dict) -> bool:
        """
        True if the transaction needs to be executed, false otherwise.

        :param request: dict The Connect Request dictionary.
        :return: bool
        """

    @abstractmethod
    def execute(self, request: dict) -> TBackgroundResponse:
        """
        BackgroundTransaction main code, contains the domain logic.

        :param request: dict The Connect Request dictionary.
        :return: TBackgroundResponse
        """

    @abstractmethod
    def compensate(self, request: dict, e: Exception) -> TBackgroundResponse:
        """
        Compensate the transaction execution on fail.

        :param request: dict The Connect Request dictionary.
        :param e: Exception The occurred error/exception.
        :return: TBackgroundResponse
        """


FnBackgroundPredicate = Callable[[dict], bool]
FnBackgroundExecution = Callable[[dict], TBackgroundResponse]
FnBackgroundCompensation = Callable[[dict, Exception], TBackgroundResponse]
FnBackgroundTransaction = Tuple[str, FnBackgroundPredicate, FnBackgroundExecution, FnBackgroundCompensation]
AnyBackgroundTransaction = Union[BackgroundTransaction, FnBackgroundTransaction]

TInteractiveResponse = TypeVar('TInteractiveResponse', bound=InteractiveResponse)


class InteractiveTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def name(self) -> str:
        """
        Provides the transaction name.

        :return: str
        """

    @abstractmethod
    def execute(self, request: dict) -> TInteractiveResponse:
        """
        Execute the main logic handling the incoming request.

        :param request: The incoming request dictionary.
        :return: TInteractiveResponse
        """


FnInteractiveExecution = Callable[[dict], TInteractiveResponse]
FnInteractiveTransaction = Tuple[str, FnInteractiveExecution]
AnyInteractiveTransaction = Union[InteractiveTransaction, FnInteractiveTransaction]


class ValidationTransaction(InteractiveTransaction, ABC):  # pragma: no cover
    @abstractmethod
    def name(self) -> str:
        """
        Provides the transaction name.

        :return: str
        """

    @abstractmethod
    def execute(self, request: dict) -> ValidationResponse:
        """
        Validates the incoming request.

        :param request: The incoming Connect Request dictionary.
        :return: ValidationResponse
        """


FnValidationExecution = Callable[[dict], ValidationResponse]
FnValidationTransaction = Tuple[str, FnValidationExecution]
AnyValidationTransaction = Union[ValidationTransaction, FnValidationTransaction]


class ScheduledTransaction(ABC):  # pragma: no cover
    @abstractmethod
    def name(self) -> str:
        """
        Provides the transaction name.

        :return: str
        """

    @abstractmethod
    def handle(self, request: dict) -> ScheduledExecutionResponse:
        """
        Handle the incoming scheduled task.

        :param request: The incoming scheduled task dictionary.
        :return: ScheduledExecutionResponse
        """


FnScheduledExecution = Callable[[dict], ScheduledExecutionResponse]
FnScheduledTransaction = Tuple[str, Callable[[dict], ScheduledExecutionResponse]]
AnyScheduledTransaction = Union[ScheduledTransaction, FnScheduledTransaction]
