from usergrid.decorators import catch_usergrid_not_found_exception
from usergrid.exceptions import UserGridException
from unittest import TestCase


class CatchUsergridNotFoundExceptionTest(TestCase):
    """
    Class to test usergrid not found exception.
    """

    def test_it_should_return_default_value_on_exception(self):
        """
        Test the decorator to return default value when there is a service not
        found exception.
        :return:
        """

        class UsergridTest():
            def __init__(self):
                pass

            @catch_usergrid_not_found_exception(return_value_on_exception=None)
            def get_entity(self, endpoint, ql=None):
                raise UserGridException(title='Service resource not found',
                                        detail="Service resource not found")

        ug = UsergridTest()

        self.assertEqual(None, ug.get_entity("stories/foo", None))

    def test_it_should_return_function_value_if_there_is_no_exception(self):
        """
        Test the decorator to  return function value when there is no service
        not found exception.
        :return:
        """

        class UsergridTest():
            def __init__(self):
                pass

            @catch_usergrid_not_found_exception(return_value_on_exception=None)
            def get_entity(self, endpoint, ql=None):
                return 1

        ug = UsergridTest()

        self.assertEqual(1, ug.get_entity("stories/foo", None))
