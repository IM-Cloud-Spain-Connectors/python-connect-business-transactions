from typing import Callable, Optional

from connect.eaas.core.responses import BackgroundResponse

from rndi.connect_business_transactions.contracts import BackgroundTransaction


class CreateCustomer(BackgroundTransaction):
    def name(self) -> str:
        return 'Create Customer'

    def should_execute(self, request: dict) -> bool:
        try:
            param = next(filter(lambda parameter: parameter['id'] == 'PARAM_CUSTOMER_ID', request['params']))
            return param.get('value', '') == ''
        except StopIteration:
            return True

    def execute(self, request: dict) -> BackgroundResponse:
        return BackgroundResponse.done()

    def compensate(self, request: dict, e: Exception) -> BackgroundResponse:
        return BackgroundResponse.done()


def should_create_subscription(request: dict) -> bool:
    try:
        param = next(filter(lambda parameter: parameter['id'] == 'PARAM_SUBS_ID', request['params']))
        return param.get('value', '') == ''
    except StopIteration:
        return True


CREATE_SUBSCRIPTION = 'Create Subscription'

def create_subscription(_: dict) -> BackgroundResponse:
    return BackgroundResponse.done()


def create_subscription_with_exception(_: dict) -> BackgroundResponse:
    raise ValueError('You shall not success!')


def create_subscription_compensate(_: dict, __: Exception) -> BackgroundResponse:
    return BackgroundResponse.fail()


class ApproveRequest(BackgroundTransaction):
    def __init__(self, execute: Optional[Callable] = None):
        self._execute = execute

    def name(self) -> str:
        return 'Approve Request'

    def should_execute(self, request: dict) -> bool:
        return request.get('status', 'pending') != 'approved'

    def execute(self, _: dict) -> BackgroundResponse:
        if self._execute is None:
            return BackgroundResponse.done()
        return self._execute(self.name())

    def compensate(self, _: dict, e: Exception) -> BackgroundResponse:
        return BackgroundResponse.fail()
