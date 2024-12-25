import maya.cmds as cmds

sel = cmds.ls(sl = True)

jnts = cmds.skinCluster(sel, inf = True, q = True)

cmds.select(jnts)