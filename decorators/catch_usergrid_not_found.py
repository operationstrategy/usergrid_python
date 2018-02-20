import functools
from usergrid.usergrid import UserGridException


def catch_usergrid_not_found_exception(return_value_on_exception=None):
    """
    decorator to catch usergrid not found exception.
    :param return_value_on_exception: default return value when there is a
           usergrid service not found exception.
    :return:
    """

    def catch_not_found_exception(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except UserGridException as ug_exception:
                if ug_exception.title == 'Service resource not found':
                    return return_value_on_exception
                raise ug_exception

        return wrapper

    return catch_not_found_exception
