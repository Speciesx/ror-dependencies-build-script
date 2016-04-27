from pyBuilder import *

class CaelumBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/ogre-caelum*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\ogre-caelum*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

cmake .. -G %(generator)s ^
 -DOgre_LIBRARY_DIRS="%(depsdir_cmake)s/libs/%(arch)s/ogre" ^
 -DOgre_INCLUDE_DIRS="%(depsdir_cmake)s/includes/%(arch)s/ogre" ^
 -DOgre_LIBRARIES=OgreMain%(debug_d)s ^
 -DCaelum_BUILD_SAMPLES=OFF
 
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\ogre-caelum*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /noconlog /p:WarningLevel=%(vswarninglevel)d /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir = self.getFirstFolder()
		res  = self.installIncludes(dir+'/main/include/*.h')
		res |= self.installIncludes(dir+'/build_%(arch)s/main/include/*.h')
		res |= self.installLibs(dir+'/lib/%(conf)s/*%(target)s*.lib')
		res |= self.installBinaries(dir+'/lib/%(conf)s/*%(target)s*.pdb', False) #optional
		res |= self.installBinaries(dir+'/lib/%(conf)s/Caelum.dll')
		return 0