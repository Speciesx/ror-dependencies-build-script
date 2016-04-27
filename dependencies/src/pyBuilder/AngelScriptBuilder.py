from pyBuilder import *

class AngelScriptBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/angelscript_*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/angelscript/projects/cmake/build_'+self.arch)
		return self.execute(r"""

cd %(path)s\sdk\angelscript\projects\cmake\build_%(arch)s
@call:checkReturnValue

cmake .. -G %(generator)s .. 
@call:checkReturnValue
""")

	def build(self):
		return self.execute(r"""
cd %(path)s\sdk\angelscript\projects\cmake\build_%(arch)s
@call:checkReturnValue

msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /noconlog /p:WarningLevel=%(vswarninglevel)d /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir  = self.getFirstFolder()
		res  = self.installIncludes(dir+'/angelscript/include/*.h')
		res |= self.installLibs(dir+'/angelscript/projects/lib/%(conf)s/*%(target)s*.lib')
		res |= self.installLibs(dir+'/angelscript/projects/cmake/build_%(arch)s/Angelscript.dir/%(conf)s/%(target)s*.pdb')
		return 0