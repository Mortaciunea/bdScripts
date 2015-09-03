
import json
import collections

eyeMarkersDict = {}
eyeMarkers = pm.ls('eye*', type='transform')
i=0
for mark in eyeMarkers:
	markerDict = {}
	markerDict['name'] = mark.name()
	markPos = mark.getTranslation(space='world')
	markerDict['position'] = [markPos.x,markPos.y,markPos.z]
	eyeMarkersDict['Marker' + str(i)] = markerDict
	i+=1

eyeTemplate = {}
eyeTemplate['Eye_Template'] = sorted(eyeMarkersDict.items())

with open('d:\\eye_template.json', mode='w') as f:
	json.dump(eyeTemplate, f,  indent = 2)
	



import pymel.core as pm
import json
with open('d:\\eye_template.json', 'r') as f:
	template = json.load( f)

print template
for token in template['Eye_Template']:
	tokenDict = token[1]
	markSphere = pm.sphere(name=tokenDict['name'],radius=0.3)
	markSphere[0].setTranslation(tokenDict['position'],space='world')
	