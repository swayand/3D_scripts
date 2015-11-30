import bpy
import os
from mathutils import Vector  
 
# weight  
w = 0.01 
 
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete(use_global=False)
 
for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)

def find_tracks_in_obj(infile, trk_prefixname="track"):
    in_file=open(infile)
    in_text=in_file.read()
    in_file.close()
    all_tracks=[]
    is_track=0
    akt_track=[]
    for akt_line in in_text.splitlines():
        if akt_line[0] is "o":
            if len(akt_track)>2:
                all_tracks.append([akt_track_name,akt_track])
            akt_track=[]
            if trk_prefixname in akt_line:
                akt_track_name=akt_line[1:].strip()
                is_track=1
            else:
                is_track=0
        if is_track:
            if akt_line[0] is "v" and akt_line[1] is not "n":
                akt_split=akt_line.split()
                akt_track.append((float(akt_split[1]),float(akt_split[2]),float(akt_split[3])))
    if len(akt_track)>2:
        all_tracks.append([akt_track_name,akt_track])
    return all_tracks



def find_boxs_in_obj(infile, trk_prefixname="Calo_ECAL"):
    in_file=open(infile)
    in_text=in_file.read()
    in_file.close()
    all_boxs=[]
    is_box=0
    akt_box=[]
    for akt_line in in_text.splitlines():
        if akt_line[0] is "o":
            if len(akt_box)>2:
                all_boxs.append([akt_box_name,akt_box])
            akt_box=[]
            if trk_prefixname in akt_line:
                akt_box_name=akt_line[1:].strip()
                is_box=1
            else:
                is_box=0
        if is_box:
            if akt_line[0] is "v" and akt_line[1] is not "n":
                akt_split=akt_line.split()
                akt_box.append((float(akt_split[1]),float(akt_split[2]),float(akt_split[3])))
    if len(akt_box)>2:
        all_boxs.append([akt_box_name,akt_box])
    return all_boxs

        

def MakePolyLine(objname, curvename, cList, origin=(0,0,0)):  
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
    curvedata.dimensions = '3D'  
    curvedata.resolution_u = 2
  
    objectdata = bpy.data.objects.new(objname, curvedata)  
    objectdata.location = origin #object origin  
    bpy.context.scene.objects.link(objectdata)  
    bpy.context.scene.objects.active = objectdata
    objectdata.select = True  

    polyline = curvedata.splines.new('NURBS')  
    #polyline = curvedata.splines.new('POLY')  
    polyline.points.add(len(cList)-1)  
    for num,coords in enumerate(cList):  
        x,y,z = coords
        polyline.points[num].co = (x,y,z,w)  
    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True

    return objectdata


def MakeBox(objname, boxname, cList, origin=(0,0,0)):  
    # Create mesh and object
    box = bpy.data.meshes.new(boxname)
    ob = bpy.data.objects.new(objname, box)
    ob.location = origin
    ob.show_name = True
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
    #  faces = ((0,1,2), (0,2,4), (7,6,5), (7,5,4), (0,4,5), )
    faces = ((0,1,2,3), (4,5,6,7), (0,3,7,4), (1,0,4,5), (1,2,6,5), (2,3,7,6))
    if len(cList) != 8:
        print("!!!!! List is not a Box with 8 points:",cList)
 
    # Create mesh from given verts, faces.
    box.from_pydata(cList, [], faces)
    # Update mesh with new data
    box.update()    
    return ob

in_file="../wavefront_obj_files/example/comp_smal.obj"



#all_tracks=find_tracks_in_obj("/autofs/users/users/wayand/when_a_fire.obj","muon_track")
all_tracks=find_tracks_in_obj(in_file)
#print(all_tracks)



for [akt_track_name,akt_track] in all_tracks:
    obj = MakePolyLine(akt_track_name, akt_track_name+"raw", akt_track)
    #obj = bpy.data.objects[akt_track_name]
    obj.data.fill_mode = 'FULL'
    obj.data.bevel_depth = 0.01
    obj.data.bevel_resolution = 5
    solidify = obj.modifiers.new(type='SOLIDIFY', name="make_solid")
    solidify.thickness = 0.01


#all_ecals=find_boxs_in_obj("/autofs/users/users/wayand/when_a_fire.obj","muon_chamb")
all_boxes=[]


all_boxes.extend(find_boxs_in_obj(in_file,"muon_chamb"))
all_boxes.extend(find_boxs_in_obj(in_file))
all_boxes.extend(find_boxs_in_obj(in_file,"Calo_HCAL"))



for [akt_ecal_name,akt_ecal] in all_boxes:
    obj = MakeBox(akt_ecal_name, akt_ecal_name+"raw",akt_ecal)





