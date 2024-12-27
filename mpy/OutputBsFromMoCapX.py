import maya.cmds as cmds
import maya.mel as mm 

objs_pose = cmds.ls(type='MCPXPose')
head_to_dup = 'Jianan_MetahumanHead'
dup_origin_pos = (200,0,0)
spacing_h = 5
spacing_v = 10 
count = 0

dup_current_pos = dup_origin_pos
bbox = cmds.exactWorldBoundingBox(head_to_dup)
sizeX = bbox[3] - bbox[0]
sizeY = bbox[4] - bbox[1]
sizeZ = bbox[5] - bbox[2]
dup_accum_h = (sizeX+spacing_h, 0, 0)
dup_accum_v = (0, 0, sizeZ+spacing_v)

if objs_pose:
    for obj in objs_pose:
        # deform
        cmds.setAttr(f"{obj}.weight", 1.0)
        # create a blend shape
        dup_head = cmds.duplicate(head_to_dup, name=f'{head_to_dup}_{obj}')[0]
        cmds.xform(dup_head, translation=dup_current_pos, worldSpace=True)
        # re-calculate pos 
        dup_current_pos = (dup_current_pos[0]+dup_accum_h[0], dup_current_pos[1]+dup_accum_h[1], dup_current_pos[2]+dup_accum_h[2])
        
        # new line 
        count += 1
        if count % 10 == 0:
            dup_current_pos = (dup_origin_pos[0]+dup_accum_v[0], dup_origin_pos[1]+dup_accum_v[1], dup_current_pos[2]+dup_accum_v[2])

        # recover deform 
        cmds.setAttr(f"{obj}.weight", 0.0)
