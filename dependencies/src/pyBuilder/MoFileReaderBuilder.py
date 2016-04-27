from pyBuilder import *

class MoFileReaderBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		res = self.unzip('files/mofilereader.zip')
		return res
		
	def configure(self):
		self.mkd('mofilereader/build/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\mofilereader\build\build_%(arch)s
@call:checkReturnValue
cmake -G %(generator)s ..
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\mofilereader\build\build_%(arch)s
@call:checkReturnValue
msbuild %(target)s.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		res  = self.installIncludes('mofilereader/include/')
		res |= self.installLibs('mofilereader/build/lib/%(conf)s/%(target)s*.lib')
		res |= self.installBinaries('mofilereader/build/lib/%(conf)s/%(target)s*.pdb', False) #optional
		return res