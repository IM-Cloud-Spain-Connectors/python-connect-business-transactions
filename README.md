# Python Connect Business Transactions

[![Test](https://github.com/othercodes/python-connect-business-transactions/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/python-connect-business-transactions/actions/workflows/test.yml)

Interface and Adapter to properly packt isolated business transactions.

## Installation

The easiest way to install the Connect Business Transaction library is to get the latest version from PyPI:

```bash
# using poetry
poetry add rndi-connect-business-transactions
# using pip
pip install rndi-connect-business-transactions
```

## The Contracts

This package provides the following contracts or interfaces:

* BackgroundTransaction
* InteractiveTransaction
* ValidationTransaction
* ScheduledTransaction

## The Adapters

The usage of the contract is quite easy, you just need to import it, extend it, and implement the required methods:

* `name`: String. Provides the transaction name.
* `should_execute`: Boolean. True if the transaction needs to be executed, false otherwise.
* `execute`: TBackgroundResponse. Transaction main code, contains the domain logic.
* `compensate`: TBackgroundResponse. Compensate the transaction execution on fail.

```python
from connect.eaas.core.responses import BackgroundResponse
from rndi.connect.business_transactions.contracts import BackgroundTransaction


class ApproveRequest(BackgroundTransaction):
    def __init__(self, client, config, logger):
        self.client = client
        self.config = config
        self.logger = logger

    def name(self) -> str:
        return 'Approve Request'

    def should_execute(self, request: dict) -> bool:
        return request.get('status', 'pending') != 'approved'

    def execute(self, request: dict) -> BackgroundResponse:
        self.client.requests[request['id']]("approve").post(payload={
            "template_id": self.config['ACTIVATION_TEMPLATE'],
        })
        return BackgroundResponse.done()

    def compensate(self, request: dict, e: Exception) -> BackgroundResponse:
        timeout = self.config.get('RESCHEDULE_TIME_LONG', 3600)
        self.logger.error("Rescheduling ({timeout}s) request {request_id} due to {reason}.".format(
            request_id=request.get('id'),
            timeout=timeout,
            reason=str(e)
        ))
        return BackgroundResponse.slow_process_reschedule(countdown=timeout)

```

Once you have the transaction stack you can use the transaction selector to get the correct transaction to apply for the
given request:

```python
from rndi.connect.business_transactions import TransactionSelector

transactions = [
    ApproveRequest(client, config, logger)
]

selected_transaction = TransactionSelector(transactions).select(request)

# finally execute the transaction.
response = selected_transaction(request)
# if any transaction match the request state a TransactionNotSelected will be raised.
```

Alternatively, you can use a functional approach to select and prepare the transaction:

```python
from rndi.connect.business_transactions import prepare, select

transactions = [
    ApproveRequest(client, config, logger)
]

selected_transaction = prepare(select(transactions, request))

# finally execute the transaction.
response = selected_transaction(request)
# if any transaction match the request state a TransactionNotSelected will be raised.
```
