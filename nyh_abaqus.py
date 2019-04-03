"""this package is for abaqus ues"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

import part
import  math
import random
import copy
import  math
import random
import copy
class Vector3D:
    def __init__(self,x=0.,y=0.,z=0.):
        self.x,self.y,self.z=x,y,z
    def __add__(self,other):
        assert isinstance(other,Vector3D)
        c=copy.deepcopy(self)
        c.x += other.x
        c.y += other.y
        c.z += other.z
        return c
    def __sub__(self,other):
        assert isinstance(other,Vector3D)
        c=copy.deepcopy(self)
        c.x -= other.x
        c.y -= other.y
        c.z -= other.z
        return c
    def __mul__(self, other):
        if isinstance(other,(float,int)):
            c = copy.deepcopy(self)
            c.x *= other
            c.y *= other
            c.z *= other
            return c
        elif isinstance(other,Vector3D):
            return self.x*other.x+self.y*other.y+self.z*other.z
        else:
            raise Exception("type error")
    @property
    def modulus(self):
        """ """
        return (self.x**2+self.y**2+self.z**2)**0.5
    @modulus.setter
    def modulus(self,v):
        assert not (self.x == 0 and self.y == 0 and self.z == 0)  # 零向量不能设定模
        assert v >= 0  # 模不能为负
        t = self.modulus
        self.x *= v / t
        self.y *= v / t
        self.z *=v/t
    @staticmethod
    def cross_product(v1,v2):
        """ """
        assert isinstance(v1,Vector3D)
        assert isinstance(v2,Vector3D)
        return Vector3D(v1.y*v2.z-v1.z*v2.y,v1.z*v2.x-v1.x*v2.z,v1.x*v2.y-v1.y*v2.x)
    @staticmethod
    def angle(v1,v2):
        """:return 0，pi"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        t=v1*v2/(v1.modulus*v2.modulus)
        return math.acos(t)


def get_edge_direction(ed):
    """
    get the direction vector of the specified edge
    :param ed:
    :return: vector3d
    """
    global p
    v=p.vertices
    assert isinstance(ed,part.EdgeType)
    i1,i2=ed.getVertices()
    x1, y1, z1 = v[i1].pointOn[0]
    x2, y2, z2 = v[i2].pointOn[0]
    return Vector3D(x2-x1,y2-y1,z2-z1)

def get_edge_length(ed):
    """

    :param ed: Edge
    :return: float
    """
    return get_edge_direction(ed).modulus

def convert_to_sequence(arg):
    """
    convert arg to sequence type in abaqus
    :param arg:edge face and their list
    :return:
    """
    global p
    if isinstance(arg,list):
        if 0==len(arg):
            raise Exception("null list")
        sample=arg[0]
    else:
        sample=arg
        arg=[sample]
    if isinstance(sample,part.EdgeType):
        cp='edges'
    elif isinstance(sample,part.FaceType):
        cp='faces'
    else:
        raise Exception("type error")
    arr=p.__getattribute__(cp)
    r=arr[sample.index:sample.index+1]
    # print(1)
    for i in range(1,len(arg)):
        r=r+arr[arg[i].index:arg[i].index+1]
    return r

def view_edge(ed,vp='Viewport: 1',groupname='last_edge_group'):
    """
    display edge(s) and save them as display_gruop nameed last_edge_group
    :param ed: edge or edge list
    :return:
    """
    sqe=convert_to_sequence(ed)
    global dgm,session
    leaf = dgm.LeafFromGeometry(edgeSeq=sqe)
    session.viewports[vp].partDisplay.displayGroup.replace(leaf=leaf)
    dg = session.viewports[vp].partDisplay.displayGroup
    dg = session.DisplayGroup(name=groupname, objectToCopy=dg)

def view_face(fa,vp='Viewport: 1',groupname='last_face_group'):
    """
    display face(s) and save them as display_gruop nameed last_edge_group
    :param fa: face or face list
    :return:
    """
    sqe=convert_to_sequence(fa)
    global dgm,session
    leaf = dgm.LeafFromGeometry(faceSeq=sqe)
    session.viewports[vp].partDisplay.displayGroup.replace(leaf=leaf)
    dg = session.viewports[vp].partDisplay.displayGroup
    dg = session.DisplayGroup(name=groupname, objectToCopy=dg)

def view_face(ed,vp='Viewport: 1',groupname='last_edge_group'):
    """
    display face(s) and save them as display_gruop nameed last_edge_group
    :param ed: edge or edge list
    :return:
    """
    sqe=convert_to_sequence(ed)
    global dgm,session
    leaf = dgm.LeafFromGeometry(edgeSeq=sqe)
    session.viewports[vp].partDisplay.displayGroup.replace(leaf=leaf)
    dg = session.viewports[vp].partDisplay.displayGroup
    dg = session.DisplayGroup(name=groupname, objectToCopy=dg)

def select_edge_by_direction(target_direct=None,tol=1,setname='selected_edge'):
    """
    select edges by direction. compare with target_direct and its reverse direction
    :param target_direct: vector3d
    :param tol: differece under this value will be thought as same direction. in degrees
    :param setname:
    :return: list of edges
    """
    global p
    lst = []
    assert isinstance(target_direct,Vector3D)
    tol=tol/180.*3.14159
    for e in p.edges:
        target_direct1 = target_direct * -1
        drt = get_edge_direction(e)
        if Vector3D.angle(drt, target_direct) < tol:
            lst.append(e)
            continue
        elif Vector3D.angle(drt, target_direct1) < tol:
            lst.append(e)
            continue
    p.Set(edges=convert_to_sequence(lst), name=setname)
    if len(lst)==0:
        print("no edges selected")
    return lst

def select_edge_by_length(minv=0.,maxv=0.,setname='selected_edge'):
    """

    :param minv:
    :param maxv: when maxv=0,maxv=minv
    :param setname:
    :return: list of edges
    """
    global p
    lst = []
    tol=1e-6
    if maxv==0:
        maxv=minv
    for e in p.edges:
        # if minv-tol<get_edge_length(e)<maxv+tol:
        if minv-tol<e.getSize(False)<maxv+tol:
            lst.append(e)
    p.Set(edges=convert_to_sequence(lst), name=setname)
    if len(lst)==0:
        print("no edges selected")
    return lst

def get_arc_by_radius(radius,setname='selected_arc'):
    """
    
    :param radius: 
    :param setname: 
    :return: 
    """
    global p
    lst = []
    tol = 1e-6
    for e in p.edges:
        try:
            r=e.getRadius()
            if abs(radius-r)<tol:
                lst.append(e)
        except Exception: # not arc
            continue
    p.Set(edges=convert_to_sequence(lst), name=setname)
    if len(lst) == 0:
        print("no arc selected")
    return lst

def select_face_by_plane(normal,point=Vector3D(0,0,0),setname='selected_face'):
    """
    select all faces which are on the specified plane
    :param normal: the normal of the plane
    :param point: a point on the plane
    :param setname:
    :return: faces list
    """
    assert isinstance(normal,Vector3D)
    lst_o=select_face_by_normal(normal,setname)
    lst=[]
    for f in lst_o:
        p1=f.pointOn[0]
        p1=Vector3D(p1[0],p1[1],p1[2])
        if abs((p1-point)*normal)<1e-6:
            lst.append(f)
    p.Set(faces=convert_to_sequence(lst), name=setname)
    if len(lst) == 0:
        print("no face selected")
    return lst

def select_face_by_normal(normal,setname='selected_face'):
    """
    select all faces whose normal are specified
    :param normal:
    :param setname:
    :return:
    """
    assert isinstance(normal, Vector3D)
    global p
    tol=1.0/180.*3.14159
    lst=[]
    for f in p.faces:
        n=f.getNormal()
        n=Vector3D(n[0],n[1],n[2])
        if Vector3D.angle(n,normal)<tol:
            lst.append(f)
    p.Set(faces=convert_to_sequence(lst), name=setname)
    if len(lst) == 0:
        print("no face selected")
    return lst







