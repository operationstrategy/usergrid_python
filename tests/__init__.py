"""
Test module
"""
import json
import os


def read_json_file(file_name):
    """
    Reads a Json file from the test_data path

    :param file_name:
    :return:
    """
    file_name = "%s/test_data/%s" % (
        os.path.dirname(os.path.realpath(__file__)),
        file_name
    )

    file_handler = open(file_name, 'r')
    json_data = json.load(file_handler)
    file_handler.close()

    return json_data
