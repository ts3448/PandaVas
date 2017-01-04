import datetime
import unittest

import requests_mock

from pycanvas import Canvas
from pycanvas.account import Account, AccountNotification, AccountReport, Role
from pycanvas.course import Course
from pycanvas.enrollment import Enrollment
from pycanvas.external_tool import ExternalTool
from pycanvas.exceptions import RequiredFieldMissing
from pycanvas.group import Group, GroupCategory
from pycanvas.user import User
from tests import settings
from tests.util import register_uris


@requests_mock.Mocker()
class TestAccount(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            requires = {'account': ['get_by_id'], 'user': ['get_by_id']}
            register_uris(requires, m)

            self.account = self.canvas.get_account(1)
            self.user = self.canvas.get_user(1)

    # __str__()
    def test__str__(self, m):
        string = str(self.account)
        assert isinstance(string, str)

    # close_notification_for_user()
    def test_close_notification_for_user_id(self, m):
        register_uris({'account': ['close_notification']}, m)

        user_id = self.user.id
        notif_id = 1
        closed_notif = self.account.close_notification_for_user(user_id, notif_id)

        assert isinstance(closed_notif, AccountNotification)
        assert hasattr(closed_notif, 'subject')

    def test_close_notification_for_user_obj(self, m):
        register_uris({'account': ['close_notification']}, m)

        notif_id = 1
        self.account.close_notification_for_user(self.user, notif_id)

    # create_account()
    def test_create_account(self, m):
        register_uris({'account': ['create_2']}, m)

        new_account = self.account.create_account()

        assert isinstance(new_account, Account)
        assert hasattr(new_account, 'id')

    # create_course()
    def test_create_course(self, m):
        register_uris({'account': ['create_course']}, m)

        course = self.account.create_course()

        assert isinstance(course, Course)
        assert hasattr(course, 'name')

    # create_subaccount()
    def test_create_subaccount(self, m):
        register_uris({'account': ['create_subaccount']}, m)

        subaccount_name = "New Subaccount"
        subaccount = self.account.create_subaccount({'name': subaccount_name})

        assert isinstance(subaccount, Account)
        assert hasattr(subaccount, 'name')
        assert subaccount.name == subaccount_name
        assert hasattr(subaccount, 'root_account_id')
        assert subaccount.root_account_id == self.account.id

    def test_create_course_missing_field(self, m):
        with self.assertRaises(RequiredFieldMissing):
            self.account.create_subaccount({})

    # create_user()
    def test_create_user(self, m):
        register_uris({'account': ['create_user']}, m)

        unique_id = 123456
        user = self.account.create_user({'unique_id': unique_id})

        assert isinstance(user, User)
        assert hasattr(user, 'unique_id')
        assert user.unique_id == unique_id

    def test_create_user_missing_field(self, m):
        with self.assertRaises(RequiredFieldMissing):
            self.account.create_user({})

    # create_notification()
    def test_create_notification(self, m):
        register_uris({'account': ['create_notification']}, m)

        subject = 'Subject'
        notif_dict = {
            'subject': subject,
            'message': 'Message',
            'start_at': '2015-04-01T00:00:00Z',
            'end_at': '2018-04-01T00:00:00Z'
        }
        notif = self.account.create_notification(notif_dict)

        assert isinstance(notif, AccountNotification)
        assert hasattr(notif, 'subject')
        assert notif.subject == subject
        assert hasattr(notif, 'start_at_date')
        assert isinstance(notif.start_at_date, datetime.datetime)

    def test_create_notification_missing_field(self, m):
        with self.assertRaises(RequiredFieldMissing):
            self.account.create_notification({})

    # delete_user()
    def test_delete_user_id(self, m):
        register_uris({'account': ['delete_user']}, m)

        deleted_user = self.account.delete_user(self.user.id)

        assert isinstance(deleted_user, User)
        assert hasattr(deleted_user, 'name')

    def test_delete_user_obj(self, m):
        register_uris({'account': ['delete_user']}, m)

        deleted_user = self.account.delete_user(self.user)

        assert isinstance(deleted_user, User)
        assert hasattr(deleted_user, 'name')

    # get_courses()
    def test_get_courses(self, m):
        required = {'account': ['get_courses', 'get_courses_page_2']}
        register_uris(required, m)

        courses = self.account.get_courses()

        course_list = [course for course in courses]
        assert len(course_list) == 4
        assert isinstance(course_list[0], Course)
        assert hasattr(course_list[0], 'name')

    # get_external_tool()
    def test_get_external_tool(self, m):
        required = {'external_tool': ['get_by_id_account']}
        register_uris(required, m)

        tool = self.account.get_external_tool(1)

        assert isinstance(tool, ExternalTool)
        assert hasattr(tool, 'name')

    # get_external_tools()
    def test_get_external_tools(self, m):
        required = {'account': ['get_external_tools', 'get_external_tools_p2']}
        register_uris(required, m)

        tools = self.account.get_external_tools()
        tool_list = [tool for tool in tools]

        assert isinstance(tool_list[0], ExternalTool)
        assert len(tool_list) == 4

    # get_index_of_reports()
    def test_get_index_of_reports(self, m):
        required = {'account': ['report_index', 'report_index_page_2']}
        register_uris(required, m)

        reports_index = self.account.get_index_of_reports("sis_export_csv")

        reports_index_list = [index for index in reports_index]
        assert len(reports_index_list) == 4
        assert isinstance(reports_index_list[0], AccountReport)
        assert hasattr(reports_index_list[0], 'id')

    # get_reports()
    def test_get_reports(self, m):
        required = {'account': ['reports', 'reports_page_2']}
        register_uris(required, m)

        reports = self.account.get_reports()

        reports_list = [report for report in reports]
        assert len(reports_list) == 4
        assert isinstance(reports_list[0], AccountReport)
        assert hasattr(reports_list[0], 'id')

    # get_subaccounts()
    def test_get_subaccounts(self, m):
        required = {'account': ['subaccounts', 'subaccounts_page_2']}
        register_uris(required, m)

        subaccounts = self.account.get_subaccounts()

        subaccounts_list = [account for account in subaccounts]
        assert len(subaccounts_list) == 4
        assert isinstance(subaccounts_list[0], Account)
        assert hasattr(subaccounts_list[0], 'name')

    # get_users()
    def test_get_users(self, m):
        required = {'account': ['users', 'users_page_2']}
        register_uris(required, m)

        users = self.account.get_users()

        user_list = [user for user in users]
        assert len(user_list) == 4
        assert isinstance(user_list[0], User)
        assert hasattr(user_list[0], 'name')

    # get_user_notifications()
    def test_get_user_notifications_id(self, m):
        required = {'account': ['user_notifs', 'user_notifs_page_2']}
        register_uris(required, m)

        user_notifs = self.account.get_user_notifications(self.user.id)

        notif_list = [notif for notif in user_notifs]
        assert len(notif_list) == 4
        assert isinstance(user_notifs[0], AccountNotification)
        assert hasattr(user_notifs[0], 'subject')

    def test_get_user_notifications_obj(self, m):
        required = {'account': ['user_notifs', 'user_notifs_page_2']}
        register_uris(required, m)

        user_notifs = self.account.get_user_notifications(self.user)

        notif_list = [notif for notif in user_notifs]
        assert len(notif_list) == 4
        assert isinstance(user_notifs[0], AccountNotification)
        assert hasattr(user_notifs[0], 'subject')

    # update()
    def test_update(self, m):
        register_uris({'account': ['update']}, m)

        self.assertEqual(self.account.name, 'Canvas Account')

        new_name = 'Updated Name'
        update_account_dict = {'name': new_name}

        self.assertTrue(self.account.update(account=update_account_dict))
        self.assertEqual(self.account.name, new_name)

    def test_update_fail(self, m):
        register_uris({'account': ['update_fail']}, m)

        self.assertEqual(self.account.name, 'Canvas Account')

        new_name = 'Updated Name'
        update_account_dict = {'name': new_name}

        self.assertFalse(self.account.update(account=update_account_dict))

    def test_list_roles(self, m):
        requires = {'account': ['list_roles', 'list_roles_2']}
        register_uris(requires, m)

        roles = self.account.list_roles()
        role_list = [role for role in roles]

        assert len(role_list) == 4
        assert isinstance(role_list[0], Role)
        assert hasattr(role_list[0], 'role')
        assert hasattr(role_list[0], 'label')

    def test_get_role(self, m):
        register_uris({'account': ['get_role']}, m)

        target_role = self.account.get_role(2)

        assert isinstance(target_role, Role)
        assert hasattr(target_role, 'role')
        assert hasattr(target_role, 'label')

    def test_create_role(self, m):
        register_uris({'account': ['create_role']}, m)

        new_role = self.account.create_role(1)

        assert isinstance(new_role, Role)
        assert hasattr(new_role, 'role')
        assert hasattr(new_role, 'label')

    def test_deactivate_role(self, m):
        register_uris({'account': ['deactivate_role']}, m)

        old_role = self.account.deactivate_role(2)

        assert isinstance(old_role, Role)
        assert hasattr(old_role, 'role')
        assert hasattr(old_role, 'label')

    def test_activate_role(self, m):
        register_uris({'account': ['activate_role']}, m)

        activated_role = self.account.activate_role(2)

        assert isinstance(activated_role, Role)
        assert hasattr(activated_role, 'role')
        assert hasattr(activated_role, 'label')

    def test_update_role(self, m):
        register_uris({'account': ['update_role']}, m)

        updated_role = self.account.update_role(2)

        assert isinstance(updated_role, Role)
        assert hasattr(updated_role, 'role')
        assert hasattr(updated_role, 'label')

    # get_enrollment()
    def test_get_enrollment(self, m):
        register_uris({'enrollment': ['get_by_id']}, m)

        target_enrollment = self.account.get_enrollment(1)

        assert isinstance(target_enrollment, Enrollment)

    def test_list_groups(self, m):
        requires = {'account': ['list_groups_context', 'list_groups_context2']}
        register_uris(requires, m)

        groups = self.account.list_groups()
        group_list = [group for group in groups]

        assert isinstance(group_list[0], Group)
        assert len(group_list) == 4

    # create_group_category()
    def test_create_group_category(self, m):
        register_uris({'account': ['create_group_category']}, m)

        name_str = "Test String"
        response = self.account.create_group_category(name=name_str)
        assert isinstance(response, GroupCategory)

    # list_group_categories()
    def test_list_group_categories(self, m):
        register_uris({'account': ['list_group_categories']}, m)

        response = self.account.list_group_categories()
        category_list = [category for category in response]
        assert isinstance(category_list[0], GroupCategory)
