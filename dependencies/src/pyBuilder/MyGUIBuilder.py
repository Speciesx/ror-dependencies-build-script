from pyBuilder import *

class MyGUIBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		res  = self.unzip('files/mygui-*.zip')
		# unpack dependencies, needed for freetype
		res |= self.unzip('files/OgreDependencies_MSVC_*.zip', self.path+'/mygui-*')
		return res
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\mygui*
@call:checkReturnValue


cd build_%(arch)s
@call:checkReturnValue

cmake .. -G %(generator)s ^
 -DMYGUI_STANDALONE_BUILD=ON^
 -DOGRE_LIB_DIR="%(depsdir_cmake)s/libs/%(arch)s/ogre/%(conf)s/" ^
 -DOGRE_INCLUDE_DIR="%(depsdir_cmake)s/includes/%(arch)s/ogre/" ^
 -DOgre_LIBRARIES=OgreMain%(debug_d)s ^
 -DMYGUI_BUILD_DEMOS=OFF ^
 -DMYGUI_BUILD_PLUGINS=OFF ^
 -DMYGUI_BUILD_TOOLS=OFF ^
 -DMYGUI_RENDERSYSTEM=3 ^
 -DMYGUI_DEPENDENCIES_DIR=Dependencies ^
 -DMYGUI_STATIC=ON
 
 
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\mygui*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir = self.getFirstFolder()
		res   = self.installIncludes(dir+'/MyGUIEngine/include/*.h')
		res  |= self.installIncludes(dir+'/Platforms/Ogre/OgrePlatform/include/*.h')
		res  |= self.installBinaries(dir+'/build_%(arch)s/bin/%(conf)s/*.exe')
		
		res |= self.installLibs(dir+'/build_%(arch)s/lib/%(conf)s/*.lib')
		res |= self.installBinaries(dir+'/build_%(arch)s/lib/%(conf)s/*.pdb', False) #optional
		res |= self.installLibs(dir+'/Dependencies/lib/%(conf)s/freetype.lib')
		res |= self.installBinaries(dir+'/Dependencies/lib/%(conf)s/*.pdb', False) #optional
		return 0