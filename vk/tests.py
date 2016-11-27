import unittest
import time

from .vkapi import VkApi
from .custom_api import (PublicApiCommands, ExecutablePublicApiCommands,
                         REQ_LIMIT_IN_EXECUTE)
from .exceptions import VkApiError
from .commands import (get_group, get_group_domen, get_group_domen_and_title,
    get_groups_under_moderation, get_groups)
from vk.private_data import test_settings


class Public:
    def __init__(self, url, domen_name, domen):
        self.url = url
        self.domen_name = domen_name
        self.domen = domen


TEST_PUBLIC = Public(
    url=test_settings.URL,
    domen_name=test_settings.DOMEN_NAME,
    domen=test_settings.DOMEN
)

BIG_PUBLIC = Public(
    url="https://vk.com/rfpl",
    domen_name="rfpl",
    domen=51812607
)


class TestComplexRequests(unittest.TestCase):
    def setUp(self):
        self.connection = VkApi(access_token="")

    def test_get_posts(self):
        params = "owner_id=-%s" % TEST_PUBLIC.domen
        items = self.connection.make_request("wall.get", params, 1)
        self.assertEqual(len(items), 1)
        items = self.connection.make_request("wall.get", params, 10)
        self.assertEqual(len(items), 10)

    def test_groupsgetById_explicit(self):
        """
        count of items id specified explicity
        """
        params = "group_id=%s" % TEST_PUBLIC.domen_name
        items = self.connection.make_request("groups.getById", params, 1)
        group = items[0]
        self.assertEqual(group["id"], TEST_PUBLIC.domen)

    def test_groupsgetById_implicit(self):
        params = "group_id=%s" % TEST_PUBLIC.domen_name
        items = self.connection.make_request("groups.getById", params)
        group = items[0]
        self.assertEqual(group["id"], TEST_PUBLIC.domen)

    def test_request_with_error(self):
        params = "group_id=%s" % "group_that_doesnot_exists123321"
        with self.assertRaises(VkApiError) as er:
            self.connection.make_request("groups.getById", params)
        self.assertEqual(er.exception.code, 100)


class TestPublicApiCommands(unittest.TestCase):
    def setUp(self):
        self.public = PublicApiCommands(access_token="", domen=TEST_PUBLIC.domen)

    def test_get_group_domen_in_apicontext(self):
        self.assertEqual(self.public.domen, TEST_PUBLIC.domen)

    def test_get_post_list(self):
        """
        count < MAX_PER_REQ
        """
        items = self.public.get_post_list(10)
        self.assertEqual(len(items), 10)

    def test_get_post_list_big_pub(self):
        # Tests the oppotunity of getting count of posts that more than max per request
        # So there we need a big public that contains enough posts
        BIG_PUBLIC = {
            "url": "https://vk.com/40kg",
            "domen_name": "40kg",
            "domen": 28627911
        }
        BIG_PUBLIC_api = PublicApiCommands(access_token="", domen=BIG_PUBLIC["domen"])

        items = BIG_PUBLIC_api.get_post_list(300)
        self.assertEqual(len(items), 300)

    def test_get_comments_form_post(self):
        posts = self.public.get_post_list(count=1)
        post = posts[0]
        comments = self.public.get_comments_form_post(post["id"])
        self.assertIsInstance(comments, list)

    def test_get_comments_from_post_list(self):
        public_with_access = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=test_settings.DOMEN)
        posts = public_with_access.get_post_list(count=15)
        comments = public_with_access.get_comments_from_post_list(posts)
        self.assertTrue(len(comments) > 0)
        self.assertTrue("likes" in comments[0])


class TestPublicApiCommandsAccessTokenRequired(unittest.TestCase):
    def setUp(self):
        self.public = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )

    def test_get_post_id_by_text(self):
        test_post = self.public.get_post_by_text(text=test_settings.TEST_POST)
        self.assertTrue("id" in test_post)
        self.assertTrue(test_settings.TEST_POST in test_post["text"])

    def test_comment_creating_and_deleting(self):
        test_post = self.public.get_post_by_text(text=test_settings.TEST_POST)
        post_id = test_post["id"]
        created_comment_id = self.public.create_comment(
            text=test_settings.TEST_COMMENT,
            post_id=post_id
        )
        comments = self.public.get_comments_form_post(post_id)
        # let's find just created comment in list of comments
        find_created_comment = [c for c in comments if c["id"] == created_comment_id][0]
        self.assertEqual(find_created_comment["id"], created_comment_id)

        self.public.delete_comment(created_comment_id)
        comments = self.public.get_comments_form_post(post_id)

        # let's check that now we are not able to find deleted comment
        find_deleted_comment = [c for c in comments if c["id"] == created_comment_id]
        self.assertTrue(len(find_deleted_comment) == 0)

    def join_and_leave_community(self):
        groups = get_groups(test_settings.ACCESS_TOKEN)

        big_public = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=BIG_PUBLIC.domen
        )
        self.assertFalse(big_public.domen in groups)
        big_public.join()
        groups = get_groups(test_settings.ACCESS_TOKEN)
        self.assertTrue(big_public.domen in groups)

        big_public.leave()
        groups = get_groups(test_settings.ACCESS_TOKEN)
        self.assertFalse(big_public.domen in groups)


class TestCommands(unittest.TestCase):
    def test_get_group_domen(self):
        domen_name = TEST_PUBLIC.domen_name
        domen = get_group_domen(domen_name)
        self.assertEqual(domen, TEST_PUBLIC.domen)

    def test_get_group_domen_and_title(self):
        domen_name = TEST_PUBLIC.domen_name
        domen, title = get_group_domen_and_title(domen_name)
        self.assertEqual(domen, TEST_PUBLIC.domen)

    def test_get_invalid_group(self):
        domen_name = "invalid_domen_name_123_123_321_321"
        with self.assertRaises(VkApiError) as er:
            get_group(domen_name)
        self.assertEqual(er.exception.code, 100)

    def test_get_moderating_groups(self):
        moderating_communities = get_groups_under_moderation(test_settings.ACCESS_TOKEN)
        self.assertIn(TEST_PUBLIC.domen, moderating_communities)

    def test_get_all_groups(self):
        groups = get_groups(test_settings.ACCESS_TOKEN)
        self.assertIn(TEST_PUBLIC.domen, groups)


class TestExecutableApiCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe_commands = ExecutablePublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )
        cls.common_commands = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )

    def test_get_comments_from_post_list(self):
        posts = self.common_commands.get_post_list(count=5)
        comments_exe = self.exe_commands.get_comments_from_post_list(posts)
        comments_com = self.common_commands.get_comments_from_post_list(posts)
        self.assertTrue(all([e for e in comments_exe if e in comments_com]))
        self.assertTrue(all([c for c in comments_com if c in comments_exe]))

        self.assertTrue("post_date" in comments_exe[0])
        self.assertTrue("post_id" in comments_exe[0])

    def test_split_posts(self):
        EXCESS = 5
        too_long_list = [i for i in range(REQ_LIMIT_IN_EXECUTE + EXCESS)]
        splited_list = self.exe_commands.split_posts(too_long_list)
        self.assertEqual(len(splited_list), 2)
        self.assertEqual(len(splited_list[0]), REQ_LIMIT_IN_EXECUTE)
        self.assertEqual(len(splited_list[1]), EXCESS)

    def test_get_comments_form_big_public(self):
        common_commands_BIG = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=BIG_PUBLIC.domen
        )
        exe_commands_BIG = ExecutablePublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=BIG_PUBLIC.domen
        )
        posts = common_commands_BIG.get_post_list(count=40)
        comments_exe = exe_commands_BIG.get_comments_from_post_list(posts)
        comments_com = common_commands_BIG.get_comments_from_post_list(posts)
        self.assertTrue(all([e for e in comments_exe if e in comments_com]))
        self.assertTrue(all([c for c in comments_com if c in comments_exe]))
        self.assertEqual(len(comments_com), len(comments_exe))


class TestExecutableApiDeleringCommentsCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe_commands = ExecutablePublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )
        cls.common_commands = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )
        test_post = cls.common_commands.get_post_by_text(text=test_settings.TEST_POST)
        cls.post_id = test_post["id"]
        cls.created_comment_id = cls.common_commands.create_comment(
            text=test_settings.TEST_COMMENT,
            post_id=cls.post_id
        )

    def test_delete_chunck_of_comments_from_comments_list(self):
        comment = {"id": self.created_comment_id}
        response_list = self.exe_commands.delete_chunck_of_comments_from_comments_list(
            limited_comments_list=[comment]
        )
        self.assertTrue(all([response == 1 for response in response_list]))

    def test_delete_comments_form_comments_list(self):
        COMMENTS_COUNT = 2
        comments_ids = []
        for _ in range(COMMENTS_COUNT):
            comment_id = self.common_commands.create_comment(
                text=test_settings.TEST_COMMENT,
                post_id=self.post_id
            )
            comments_ids.append(comment_id)
        comments = [{"id": comment_id} for comment_id in comments_ids]
        response_list = self.common_commands.delete_comments(comments)

        self.assertTrue(all([response == 1 for response in response_list]))
        self.assertTrue(len(response_list) == COMMENTS_COUNT)


class TestUnixTimestampInVK(unittest.TestCase):
    """
    Checks that unix timestamp in vk is the same that in datetime

    """
    @classmethod
    def setUpClass(cls):
        cls.public = PublicApiCommands(
            access_token=test_settings.ACCESS_TOKEN,
            domen=TEST_PUBLIC.domen
        )
        test_post = cls.public.get_post_by_text(text=test_settings.TEST_POST)
        cls.post_id = test_post["id"]

    def test_create_post_and_check_unixts(self):
        creation_ts = time.time()
        comment_id = self.public.create_comment(
            text=test_settings.TEST_COMMENT,
            post_id=self.post_id
        )
        comments = self.public.get_comments_form_post(self.post_id)
        created_comment = [comment for comment in comments if comment["id"] == comment_id]
        created_comment = created_comment[0]

        MAX_DELAY_IN_SEC = 10
        self.assertTrue(creation_ts - created_comment["date"] < MAX_DELAY_IN_SEC)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
