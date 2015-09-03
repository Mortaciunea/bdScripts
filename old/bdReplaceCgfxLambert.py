import pymel.core as pm



def bdSetUpLamberts():
	cgfxShaders = pm.ls(type='cgfxShader')
	for cgfx in cgfxShaders:
		diffuseFile = pm.listConnections('%s.diffuseMapSampler'%cgfx)[0]
		shaderNode = pm.listConnections('%s.outColor'%cgfx)[0]
		#transparancyFile = pm.listConnections('%s.specularMapSampler'%cgfx)[0]
		lambertNode = pm.shadingNode('lambert',asShader=1,n=cgfx.name() + '_LMB' )
		diffuseFile.outColor.connect(lambertNode.color)
		
		cgfx.outColor.disconnect()
		lambertNode.outColor.connect(shaderNode.surfaceShader)
	


def bdSetupMeshes():
	meshes = pm.ls(type='mesh')
	
	for mesh in meshes:
		if ('Orig' not in mesh.name()) and ('ground' not in mesh.name()) and ('reflection' not in mesh.name()):
			mesh.primaryVisibility.set(0)
			mesh.castsShadows.set(0)
			
		elif('ground' in mesh.name()):
			mesh.primaryVisibility.set(0)
			mesh.visibleInReflections.set(0)
			mesh.visibleInRefractions.set(0)
			mesh.castsShadows.set(0)
			mesh.receiveShadows.set(0)

#bdSetUpLamberts()
#bdSetupMeshes()