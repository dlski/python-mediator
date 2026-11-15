from typing import Any


class RequestExecutor:
    """
    Request executor interface.
    """

    async def execute(self, obj: Any, **kwargs) -> Any:
        """
        Executes given request and returns execution result.
        :param obj: request object
        :param kwargs: optional extra arguments
        :return: request execution result
        """
        raise NotImplementedError
