from pyBuilder import *

class CurlBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/curl-*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\curl*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

cmake -G %(generator)s ..
@call:checkReturnValue
""")
			
	def build(self):
		return self.execute(r"""
cd %(path)s\curl*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

msbuild %(target)s.sln /t:libcurl /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			
	def install(self):
		dir = self.getFirstFolder()
		res  = self.installIncludes(dir+'/include/curl/*.h', True, 'curl')
		res |= self.installIncludes(dir+'/build_%(arch)s/lib/curl_config.h')
		res |= self.installBinaries(dir+'/build_%(arch)s/lib/%(conf)s/libcurl.dll')
		res |= self.installBinaries(dir+'/build_%(arch)s/lib/%(conf)s/libcurl.pdb', False)
		res |= self.installLibs(dir+'/build_%(arch)s/lib/Release/libcurl_imp.lib')
		return res