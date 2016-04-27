from pyBuilder import *

class PagedGeometryBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/ogre-pagedgeometry*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\ogre-pagedgeometry*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

cmake .. -G %(generator)s ^
 -DOgre_LIBRARY_DIRS="%(depsdir_cmake)s/libs/%(arch)s/ogre/%(conf)s/" ^
 -DOgre_INCLUDE_DIRS="%(depsdir_cmake)s/includes/%(arch)s/ogre/" ^
 -DOgre_LIBRARIES=OgreMain%(debug_d)s ^
 -DPAGEDGEOMETRY_USE_OGRE_RANDOM=ON ^
 -DPAGEDGEOMETRY_BUILD_SAMPLES=OFF ^
 -DPAGEDGEOMETRY_USER_DATA=ON
 
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\ogre-pagedgeometry*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /p:WarningLevel=%(vswarninglevel)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir  = self.getFirstFolder()
		res  = self.installIncludes(dir+'/include/*.h')
		res |= self.installIncludes(dir+'/build_%(arch)s/include/*.h')
		res |= self.installLibs(dir+'/lib/%(conf)s/*%(target)s*.lib')
		res |= self.installLibs(dir+'/build_%(arch)s/source/PagedGeometry.dir/%(conf)s/*%(target)s*.pdb')
		return 0