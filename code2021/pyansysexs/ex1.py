import os
import pyansys

path = "e:\\ansysfile"
mapdl = pyansys.launch_mapdl(run_location=path, interactive_plotting=False)

# create a square area using keypoints
mapdl.prep7()
mapdl.k(1, 0, 0, 0)
mapdl.k(2, 1, 0, 0)
mapdl.k(3, 1, 1, 0)
mapdl.k(4, 0, 1, 0)
mapdl.l(1, 2)
mapdl.l(2, 3)
mapdl.l(3, 4)
mapdl.l(4, 1)
mapdl.et(1,188)
mapdl.mp('ex',1,3.5e10)
mapdl.mp('nuxy',1,0.2)
mapdl.mp('dens',1,2500)
mapdl.sectype(1,'beam','csolid')
mapdl.secoffset('cent')
mapdl.secdata(0.05)
mapdl.latt(1,0,1,0,0,1)
mapdl.lesize('all',0.1)
mapdl.lmesh('all')
mapdl.dk(1,'all',0)
mapdl.finish()
mapdl.slashsolu()#进入求解模块
mapdl.acel(5,5,5)
mapdl.solve()
mapdl.finish()
result=mapdl.result
ndnum,ndisp=result.nodal_displacement(0) #0代表第一个dataframe
mapdl.save()