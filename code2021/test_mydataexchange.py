from unittest import TestCase,main

from code2021.mydataexchange import make_data_from_paragraph
from vector3d import Vector3D


class Test(TestCase):
    def test_make_data_from_paragraph(self):
        paragraph = """


        a1 float 12.32
        s1 string iam a dog
        v1 vector 123,23.1,3"""
        d = make_data_from_paragraph(paragraph)
        self.assertEqual(12.32,d['a1'])
        self.assertEqual("iam a dog", d['s1'])
        self.assertEqual(Vector3D(123,23.1,3), d['v1'])


if __name__ == '__main__':
    main()
