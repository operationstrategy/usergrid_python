from usergrid.mock_usergrid import MockUserGrid
import time
import uuid
import unittest
import logging

'''
This is a little sanity checking on the mock object
'''


class TestMockUserGrid(unittest.TestCase):
    channels = {}
    stories = {}

    def setUp(self):
        self.ug = MockUserGrid()
        self.ug.login()
        # self.add_channels()
        # self.add_stories()
        logging.getLogger(__name__).disabled = True

    ################# TESTS ###########################
    def test_basic_get(self):
        chid = uuid.uuid1()
        self.add_channel(chid, "Test Channel {0}".format(chid))

        ch = self.ug.get_entity("/channels/{0}".format(chid))
        self.assertEqual(ch, self.channels[chid])

    def test_basic_get_multiple(self):
        chid1 = uuid.uuid1()
        chid2 = uuid.uuid1()
        self.add_channel(chid1, "Test Channel 1")
        self.add_channel(chid2, "Test Channel 2")
        self.ug.add_response("/channels",
                             data=[self.channels[chid1], self.channels[chid2]])

        channels = self.ug.collect_entities("/channels")

    ################## SETUP ##########################
    def add_channels(self):
        ch1uuid = uuid.uuid1()
        self.add_channel(ch1uuid, "Channel 1")

    def add_channel(self, chid, text):
        now = int(time.time()) * 1000
        channel = {
            'name': text,
            'uuid': chid,
            'created': now,
            'modified': now,
            'description': "{0} Description".format(text),
            'title': '{0} Title'.format(text)
            ,
            'type': 'channels'
        }

        self.ug.add_response("/channels/{0}".format(chid), data=channel)
        self.channels[chid] = channel

    def add_stories(self):
        story1uuid = uuid.uuid1()
        self.add_story(story1uuid, "Story 1")

    def add_story(self, storyid, text, chid=None):
        now = int(time.time()) * 1000
        story = {
            'audio': 'unimplemented',
            'audiointro': 'unimplemented',
            'created': now,
            'description': '{0} Description'.format(text),
            'descriptor': '{0} Descriptor'.format(text),
            'duration': 180,
            'hls': {
                'playlist': 'unimplemented',
                'processed_at': now,
                'status': 'complete',
                'status_update': now
            },
            'image': 'unimplemented',
            'image_cdn': None,
            'intro_hls': None,
            'metadata': {
                'connecting': {
                    'contains': '/stories/{0}/connecting/contains'.format(
                        storyid),
                    'owns': 'unimplemented'
                },
                'connections': {
                    'has': 'unimplemented',
                    'hasintro': 'unimplemented'
                }
            },
            'modified': now,
            'name': '{0} Name'.format(text),
            'owner': 'unimplemented',
            'relatedStories': {
                'global': [],
                'last_processed': now
            },
            'status': {
                'audio': 'complete',
                'audioIntro': 'complete',
                'picture': 'complete'
            },
            'tags': [],
            'title': '{0} Title'.format(text),
            'type': 'stories',
            'uuid': storyid
        }

        if chid:
            story['channels'] = ["{0}".format(chid)]
            story['channel_feeds'] = {
                chid: 0
            }

        self.ug.add_response("/stories/{0}".format(storyid), data=story)
        self.stories[storyid] = story


if __name__ == '__main__':
    unittest.main()
