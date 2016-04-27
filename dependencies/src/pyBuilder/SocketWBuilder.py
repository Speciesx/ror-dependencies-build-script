from pyBuilder import *

class SocketWBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/socketw.zip')
		
	def configure(self):
		self.mkd('socketw/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\socketw\build_%(arch)s
@call:checkReturnValue

cmake -G %(generator)s ..
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\socketw\build_%(arch)s
@call:checkReturnValue
msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		res  = self.installIncludes('socketw/src/*.h')
		res |= self.installLibs('socketw/build_%(arch)s/%(conf)s/*%(target)s*.lib')
#		res |= self.installBinaries('socketw/build_%(arch)s/%(conf)s/*%(target)s*.pdb', False) #optional
		return res