from pyBuilder import *

class OISBuilder(BuildTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/ois*.zip')
		
	def configure(self):
		return 0
			
	def build(self):
		res = 0
		for config in ['Debug', 'Release']:
			if not config in CONFIGURATIONS:
				continue

			self.configuration = config
			
			if 'x86' in PLATFORMS:
				self.platform='Win32'
				res |= self.execute(r"""
cd %(path)s\ois*
@call:checkReturnValue
cd Win32
@call:checkReturnValue
msbuild ois_vc14.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
			if 'x64' in PLATFORMS:
				self.platform='x64'
				res |= self.execute(r"""
cd %(path)s\ois*
@call:checkReturnValue
cd Win32
@call:checkReturnValue
msbuild ois_vc14.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
		return res
			
	def install(self):
		dir = self.getFirstFolder()
		res = self.installIncludes(dir+'/includes/*')
		if 'x86' in PLATFORMS:
			self.arch = 'x86'
			if 'Release' in CONFIGURATIONS:
				self.configuration = 'Release'
				res |= self.installLibs(dir+'/lib/ois_static.lib')
			if 'Debug' in CONFIGURATIONS:
				self.configuration = 'Debug'
				res |= self.installLibs(dir+'/lib/ois_static_d.lib')
		if 'x64' in PLATFORMS:
			self.arch = 'x64'
			if 'Release' in CONFIGURATIONS:
				self.configuration = 'Release'
				res |= self.installLibs(dir+'/lib64/ois_static.lib')
			if 'Debug' in CONFIGURATIONS:
				self.configuration = 'Debug'
				res |= self.installLibs(dir+'/lib64/ois_static_d.lib')
		return res