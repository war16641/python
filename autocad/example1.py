"""
先打开2018cad，新建一个空白文档，或者打开一个文档就可以运行,2016cad不行。

"""


from pyautocad import Autocad,APoint

acad=Autocad(create_if_not_exists=True)
acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)

p1=APoint(0,0)
p2=APoint(50,25)
for i in range(0,5):
    text=acad.model.AddText('Hi %s' %i,p1,2.5)
    acad.model.AddLine(p1,p2)
    acad.model.AddCircle(p1,10)
    p1.y+=10

dp=APoint(10,0)
for text in acad.iter_objects('Text'):
    print('text: %s at: %s' %(text.TextString,text.InsertionPoint))
    text.InsertionPoint=APoint(text.InsertionPoint)+dp
    # text.TextString="123" #改变text的文字
for obj in acad.iter_objects(['Circle','Line']):
    print(obj.ObjectName)