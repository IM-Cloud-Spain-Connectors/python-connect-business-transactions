import pytest
from connect.eaas.core.responses import BackgroundResponse
from rndi.connect.business_transactions.adapters import TransactionSelector
from rndi.connect.business_transactions.exceptions import InvalidTransaction, TransactionNotSelected
from tests.sample import (
    ApproveRequest,
    CREATE_SUBSCRIPTION,
    create_subscription,
    create_subscription_compensate,
    create_subscription_with_exception,
    CreateCustomer,
    should_create_subscription,
)


def test_transaction_selector_should_select_transaction_and_success_execution_for_class_transaction():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
            {'id': 'PARAM_SUBS_ID', 'value': 'bc180aa9-4a41-4c5e-ad0d-656f1dc0c6d9'},
        ],
    }

    def assert_correct_transaction(name: str):
        assert name == 'Approve Request'
        return BackgroundResponse.done()

    ts = TransactionSelector([
        CreateCustomer(),
        (CREATE_SUBSCRIPTION, should_create_subscription, create_subscription),
        ApproveRequest(assert_correct_transaction),
    ])

    transaction = ts.select(request)
    assert callable(transaction)
    assert transaction(request).status == 'success'


def test_transaction_selector_should_select_transaction_and_fail_execution_for_class_transaction():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
            {'id': 'PARAM_SUBS_ID', 'value': 'bc180aa9-4a41-4c5e-ad0d-656f1dc0c6d9'},
        ],
    }

    def assert_correct_transaction(name: str):
        assert name == 'Approve Request'
        raise ValueError('You shall not success!')

    ts = TransactionSelector([
        CreateCustomer(),
        (CREATE_SUBSCRIPTION, should_create_subscription, create_subscription),
        ApproveRequest(assert_correct_transaction),
    ])

    transaction = ts.select(request)
    assert callable(transaction)
    assert transaction(request).status == 'fail'


def test_transaction_selector_should_select_transaction_and_success_execution_for_fn_transaction():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
            {'id': 'PARAM_SUBS_ID'},
        ],
    }

    ts = TransactionSelector([
        CreateCustomer(),
        (CREATE_SUBSCRIPTION, should_create_subscription, create_subscription),
        ApproveRequest(),
    ])

    transaction = ts.select(request)
    assert callable(transaction)
    assert transaction(request).status == 'success'


def test_transaction_selector_should_select_transaction_and_fail_execution_for_fn_transaction_with_compensation():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
            {'id': 'PARAM_SUBS_ID'},
        ],
    }

    ts = TransactionSelector([
        CreateCustomer(),
        (CREATE_SUBSCRIPTION, should_create_subscription, create_subscription_with_exception),
        ApproveRequest(),
    ])

    transaction = ts.select(request)
    assert callable(transaction)

    with pytest.raises(ValueError):
        transaction(request)


def test_transaction_selector_should_select_transaction_and_fail_execution_for_fn_transaction_without_compensation():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
            {'id': 'PARAM_SUBS_ID'},
        ],
    }

    ts = TransactionSelector([
        CreateCustomer(),
        (CREATE_SUBSCRIPTION, should_create_subscription, create_subscription_with_exception,
         create_subscription_compensate),
        ApproveRequest(),
    ])

    transaction = ts.select(request)
    assert callable(transaction)
    assert transaction(request).status == 'fail'


def test_transaction_selector_should_raise_exception_on_invalid_transaction():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
        ],
    }

    ts = TransactionSelector([CreateCustomer])

    with pytest.raises(InvalidTransaction):
        ts.select(request)


def test_transaction_selector_should_raise_exception_on_transaction_not_selected():
    request = {
        'status': 'pending',
        'params': [
            {'id': 'PARAM_CUSTOMER_ID', 'value': 'eda1b4f1-a3a8-4a87-bd3f-ad71f6c2e93e'},
        ],
    }

    ts = TransactionSelector([])

    with pytest.raises(TransactionNotSelected):
        ts.select(request)
