from pyBuilder import *

class OgreBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		res  = self.unzip('files/ogre_src_*.zip')
		res |= self.unzip('files/OgreDependencies_MSVC_*.zip', self.path+'/ogre_*')
		return res

	def configure(self):
		return self.execute(r"""
cd %(path)s\ogre_src*
call:checkReturnValue

mkdir build_%(arch)s
cd build_%(arch)s
call:checkReturnValue

cmake .. -G %(generator)s ^
 -DOGRE_BUILD_RENDERSYSTEM_D3D9=ON ^
 -DOGRE_BUILD_RENDERSYSTEM_D3D11=OFF ^
 -DOGRE_BUILD_RENDERSYSTEM_GL=ON ^
 -DOGRE_BUILD_RENDERSYSTEM_GL3PLUS=OFF ^
 -DOGRE_BUILD_COMPONENT_VOLUME=OFF ^
 -DOGRE_BUILD_SAMPLES=OFF ^
 -DOGRE_BUILD_TOOLS=ON ^
 -DOGRE_CONFIG_ALLOCATOR=4 ^
 -DOGRE_CONFIG_CONTAINERS_USE_CUSTOM_ALLOCATOR=ON ^
 -DOGRE_CONFIG_DOUBLE=OFF
call:checkReturnValue
""")

	def build(self):
		return self.execute(r"""
cd %(path)s\ogre_src*
call:checkReturnValue
cd build_%(arch)s
call:checkReturnValue

msbuild ogre.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
call:checkReturnValue
""")

	def install(self):
		dir = self.getFirstFolder()
		res  = self.installIncludes(dir+'/build_%(arch)s/include/')
		res |= self.installIncludes(dir+'/OgreMain/include/*')		
		res |= self.installIncludes(dir+'/Components/Paging/include/*', True, 'Paging')
		res |= self.installIncludes(dir+'/Components/Property/include/*', True, 'Property')
		res |= self.installIncludes(dir+'/Components/RTShaderSystem/include/*', True, 'RTShaderSystem')
		res |= self.installIncludes(dir+'/Components/Terrain/include/*', True, 'Terrain')
		res |= self.installIncludes(dir+'/Components/Overlay/include/*', True, 'Overlay')
		res |= self.installIncludes(dir+'/PlugIns/ParticleFX/include/*', True, 'Plugins/ParticleFX')
		res |= self.installLibs(dir+'/build_%(arch)s/lib/%(conf)s/Ogre*.lib')
		#res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/cg.dll')
		res |= self.installBinaries(dir+'/Dependencies/bin/Release/cg.dll')
		res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/Ogre*.dll')
		#res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/Ogre*.pdb', False) #optional
		res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/Plugin_*.dll')
		#res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/Plugin_*.pdb', False) #optional
		res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/RenderSystem_*.dll')
		#res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/RenderSystem_*.pdb', False) #optional
		res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/*.exe')
		res |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/*.pdb', False) #optional
		return res