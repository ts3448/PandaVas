from __future__ import absolute_import, division, print_function, unicode_literals
import unittest

import requests_mock

from canvasapi import Canvas
from canvasapi.rubric import RubricAssociation
from tests import settings
from tests.util import register_uris


@requests_mock.Mocker()
class TestGradingStandard(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            register_uris({"course": ["get_by_id", "get_rubric_single"]}, m)

            self.course = self.canvas.get_course(1)
            self.rubric = self.course.get_rubric(1)

    # __str__()
    def test__str__(self, m):
        string = str(self.rubric)
        self.assertIsInstance(string, str)


@requests_mock.Mocker()
class TestRubricAssociation(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

        with requests_mock.Mocker() as m:
            register_uris(
                {
                    "course": [
                        "get_by_id",
                        "create_rubric_with_association",
                        "create_rubric_association",
                    ]
                },
                m,
            )

            self.course = self.canvas.get_course(1)
            self.rubric = self.course.create_rubric()
            self.association = self.course.create_rubric_association()

    # __str__()
    def test__str__(self, m):
        string = str(self.rubric["rubric_association"])
        self.assertIsInstance(string, str)

    # update
    def test_update(self, m):
        register_uris({"rubric": ["update_rubric_association"]}, m)

        rubric_association = self.association.update()

        self.assertIsInstance(rubric_association, RubricAssociation)
        self.assertEqual(rubric_association.id, 5)
        self.assertEqual(rubric_association.association_type, "Assignment")

    # delete
    def test_delete(self, m):
        register_uris({"rubric": ["delete_rubric_association"]}, m)

        rubric_association = self.association.delete()

        self.assertIsInstance(rubric_association, RubricAssociation)
        self.assertEqual(rubric_association.id, 4)
        self.assertEqual(rubric_association.association_type, "Assignment")
