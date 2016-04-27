from pyBuilder import *

class OpenALSoftBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/openal-soft-*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\openal*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

cmake -G %(generator)s ..
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\openal*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

msbuild OpenAL.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir = self.getFirstFolder()
		res  = self.installIncludes(dir+'/include/*')
		res |= self.installLibs(dir+'/build_%(arch)s/%(conf)s/OpenAL32.lib')
		res |= self.installBinaries(dir+'/build_%(arch)s/%(conf)s/OpenAL32.pdb', False)
		res |= self.installBinaries(dir+'/build_%(arch)s/%(conf)s/OpenAL32.dll')
		res |= self.installBinaries(dir+'/build_%(arch)s/%(conf)s/openal-info.exe')
		return res