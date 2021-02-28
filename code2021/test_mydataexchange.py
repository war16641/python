from unittest import TestCase,main
from math import pi
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from code2021.mydataexchange import make_data_from_paragraph,toline,read_single_line
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from code2021.MyGeometric.rect import Rect
from vector3d import Vector3D


class Test(TestCase):
    def test_make_data_from_paragraph(self):
        paragraph = """


        a1 float 12.32
        s1 string iam a dog
        v1 vector 123,23.1,3
    
        r2 rect 1,1,0,5,5,0
        elo1 lineseg 0,1,0,2,1,0
        arc1 arc 1,1,0,1,0,3
        pl1 polyline 3
        _ lineseg 0,0,0,1,0,0
        _ lineseg 1,0,0,1,1,0
        _ arc 0,1,0,1,0,3.14159
        """
        d = make_data_from_paragraph(paragraph)
        self.assertEqual(12.32,d['a1'])
        self.assertEqual("iam a dog", d['s1'])
        self.assertEqual(Vector3D(123,23.1,3), d['v1'])

        self.assertEqual(25, d['r2'].area)
        elo=LineSegment(Vector3D(0,1),Vector3D(2,1))
        self.assertTrue(elo==d['elo1'])
        a=Arc(Vector3D(1,1),1,0,3)
        self.assertTrue(a==d['arc1'])
        self.assertTrue(isinstance(d['pl1'],PolyLine))
        self.assertEqual(3,len(d['pl1'].segs))

    def test_toline(self):
        v=Vector3D(1,2.1,3.1)
        _,_,v1=read_single_line(toline(v,"_"))
        self.assertTrue(v==v1)

        elo=LineSegment(Vector3D(1,2.1),Vector3D(10,10.1))
        _,_,elo1=read_single_line(toline(elo,"_"))
        self.assertTrue(elo==elo1)

        arc=Arc(Vector3D(0,1),1,0,1.1)
        _,_,arc1=read_single_line(toline(arc,"_"))
        self.assertTrue(arc == arc1)
        arc=Arc(Vector3D(0,1),1,0,-1.1)
        _,_,arc1=read_single_line(toline(arc,"_"))
        self.assertTrue(arc == arc1)


        elo1=LineSegment(Vector3D(0,0),Vector3D(1,0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a=Arc(Vector3D(0,1),1,0,pi)
        pl=PolyLine([elo1,elo2,a])
        line="""pl1 polyline 3
_ lineseg 0.000000,0.000000,0.000000,1.000000,0.000000,0.000000
_ lineseg 1.000000,0.000000,0.000000,1.000000,1.000000,0.000000
_ arc 0.000000,1.000000,0.000000,1.000000,0.000000,3.14159265358979"""
        d=make_data_from_paragraph(line,0)
        t=pl==d['pl1']
        self.assertTrue(t)

if __name__ == '__main__':
    main()
