import ifcopenshell
import ifcopenshell.geom
from pathlib import Path
import math
import argparse
import json


# Create the argument parser
parser = argparse.ArgumentParser(description='Description of your program.')
# Add the input argument
parser.add_argument('--input', help='Path to the input file.')
# Add the output argument
parser.add_argument('--output', help='Path to the output file.')
# Parse the command-line arguments
args = parser.parse_args()

def distance3d(p1, p2):
    return(math.sqrt(pow(p1[0]-p2[0],2)+pow(p1[1]-p2[1],2)+pow(p1[2]-p2[2],2)))

def distance2d(p1, p2):
    return(math.sqrt(pow(p1[0]-p2[0],2)+pow(p1[1]-p2[1],2)))


ifcpath = args.input
ifcpath = ifcpath.replace("\\","\\\\")
#print('in Py het pad: '+ifcpath)

model = ifcopenshell.open(ifcpath)
ListofRamps = model.by_type('IfcRampFlight')
print('Found '+str(len(ListofRamps))+' ramps.')

if(len(ListofRamps)==0):
    data = {"comment" : "no ramps found"}

else:
    resobj = []
    for k in range(0,len(ListofRamps)):
        ramp = ListofRamps[k]
        #print(ramp.id)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, ramp)
        verts = shape.geometry.verts
        grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
        #print(grouped_verts)

        #sorting the vertices by equals x and Y, suppositon is that the (rectangular!) ramp is defined by 8 vertices
        equalxy_verts = []
        for j in range(0,4):
            first_vert = grouped_verts[0]
            equalxy_verts.append(first_vert)
            grouped_verts.remove(first_vert)
            vert_to_remove = []
            for i in range(0, len(grouped_verts)):
                if(equalxy_verts[j*2][0]==grouped_verts[i][0] and equalxy_verts[j*2][1]==grouped_verts[i][1]):
                    equalxy_verts.append(grouped_verts[i])
                    vert_to_remove = grouped_verts[i]
            if(grouped_verts.__contains__(vert_to_remove)):
                grouped_verts.remove(vert_to_remove)
        #print(len(equalxy_verts))
        #print(equalxy_verts)

        #extracting the vertices with highest z value for equal x and y, resulting in 4 vertices defining the upper surface of the ramp
        highestz_vert = []
        for j in range(0,4):
            highestz = equalxy_verts[j*2]
            if(highestz[2]<equalxy_verts[j*2+1][2]):
                highestz=equalxy_verts[j*2+1]
            highestz_vert.append(highestz)
        #print(len(highestz_vert))
        #print(highestz_vert)

        #sorting by equal z 
        sortedz_vert = []
        sortedz_vert.append(highestz_vert[0])
        highestz_vert.remove(sortedz_vert[0])
        equalZ = []
        for i in range(0,len(highestz_vert)):
            if(highestz_vert[0][2]==highestz_vert[i][2]):
                equalZ = highestz_vert[i]
                sortedz_vert.append(equalZ)  
        highestz_vert.remove(equalZ)
        sortedz_vert.append(highestz_vert[0])
        sortedz_vert.append(highestz_vert[1])
        #print(len(sortedz_vert))
        #print(sortedz_vert)

        rampwidth = distance3d(sortedz_vert[0],sortedz_vert[1])
        horizontal = distance2d(sortedz_vert[0],sortedz_vert[2])
        if(horizontal>distance2d(sortedz_vert[0],sortedz_vert[3])):
            horizontal = distance2d(sortedz_vert[0],sortedz_vert[3])
        rampheight = abs(sortedz_vert[0][2]-sortedz_vert[2][2])

        rampresults = {
            "id" : str(ramp.Name),
            "width" : str(round(rampheight/horizontal,3)),
            "length" : str(round(horizontal,3)),
            "height" : str(round(rampheight,3)),
            "slope" : str(round(rampheight/horizontal,3))
        }
        resobj.append(rampresults)
    data = resobj
    #print(data)
    
jsonpath = "views/json/dump"
with open(jsonpath, "w") as json_file:
    json.dump(data, json_file)
