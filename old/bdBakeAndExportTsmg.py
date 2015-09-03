import pymel.core as pm
import os
from tsmgame.scripts.prepForExport import prepCharactersForExport 

def bdBakeAndExport():
	sceneRef = pm.listReferences()
	for ref in sceneRef:
		if 'paddington' in ref.namespace:
			ref.replaceWith('P:/paddington/working_project/scenes/characters/paddington/03_rigging/01_wip/x_rig_paddington_v50.ma')
		ref.importContents(removeNamespace=1)
	startFrame = int(pm.playbackOptions(q=1,ast=1))
	endFrame = int(pm.playbackOptions(q=1,aet=1))
	
	print 'Exporting for Ogre'
	bakeBScommand = 'bakeResults -simulation true -t "' + str(startFrame) +':' + str(endFrame) +'" -sampleBy 1 -disableImplicitControl true -preserveOutsideKeys false -sparseAnimCurveBake true -removeBakedAttributeFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"head_BS"}'
	pm.mel.eval(bakeBScommand)

	prepCharactersForExport()
	
	sceneName = pm.sceneName().split('/')[-1].split('.')[0].split('_')
	clipName = '_'.join(sceneName[:5])
	
	
	clipName += ('_' + str(endFrame))
	print clipName 
	
	command1 = 'ogreExport -all -outDir "P:/paddington/assets/characters/paddington_std/animations/" -skeletonClip "' + clipName + '" startEnd ' + str(startFrame) + ' ' + str(endFrame) + ' frames sampleByFrames 1 -lu pref -scale 1.00 -skeletonAnims -skelBB -np bindPose'
	
	pm.mel.eval(command1)

	command2 = 'ogreExport -outDir "P:/paddington/assets/characters/paddington_std" -all -lu pref -scale 1.00 -mesh "P:/paddington/assets/characters/paddington_std/paddington_basic.mesh" -n -bn -v -t -tangents TANGENT -preventZeroTangent 100.0 -mat "P:/paddington/assets/characters/paddington_std/materials/paddington_basic.material" -blendShapes -BSAnims -BSClip ' + clipName + ' startEnd ' + str(startFrame) + ' ' + str(endFrame) + ' frames sampleByFrames 1 -optimizePoseAnimation -vertexAnimSets -vertexAnimSetFileName "P:/paddington/assets/characters/paddington_std/animations/' + clipName + '.vas"'
	pm.mel.eval(command2)