from pyBuilder import *

class WxWidgetsBuilder(BuildTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/wxWidgets-*.zip')
		
	def configure(self):
		return 0
			
	def build(self):
		global PLATFORMS, CONFIGURATIONS
		res = 0
		for config in ['Release']: #'Debug', 
			dstr = ''
			if config == 'Debug': dstr = 'd'
			
			if not config in CONFIGURATIONS:
				continue

			self.configuration = config
			
			if 'x86' in PLATFORMS:
				self.platform='Win32'
				self.arch = 'x86'
				self.banner(self.target + ' / ' + self.configuration + ' / ' + self.arch + ' / ' + self.platform, '{gb}')
				res |= self.execute(r"""
cd %(path)s\wxWidgets-*
@call:checkReturnValue

cd build\msw
@call:checkReturnValue

msbuild wx_vc14.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
				dir = self.getFirstFolder()
				res |= self.installIncludes(dir+'/include/wx', True, 'wx')
				res |= self.installIncludes(dir+'/lib/vc_lib/mswu/wx', True, 'wx')
				res |= self.installLibs(dir+'/lib/vc_lib/*.lib')
				res |= self.installLibs(dir+'/lib/vc_lib/*.pdb', True)
			
			if 'x64' in globals()['PLATFORMS']:
				self.platform='x64'
				self.arch = 'x64'
				self.banner(self.target + ' / ' + self.configuration + ' / ' + self.arch + ' / ' + self.platform, '{gb}')
				res |= self.execute(r"""
				
cd %(path)s\wxWidgets-*
@call:checkReturnValue

cd build\msw
@call:checkReturnValue

msbuild wx_vc14.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")
				dir = self.getFirstFolder()
				res |= self.installIncludes(dir+'/include/wx', True, 'wx')
				res |= self.installIncludes(dir+'/lib/vc_x64_lib/mswu/wx', True, 'wx')
				res |= self.installLibs(dir+'/lib/vc_x64_lib/*.lib')
				res |= self.installLibs(dir+'/lib/vc_x64_lib/*.pdb', True)
		return res
			
	def install(self):
		# since angelscript solution clears some targets, we have to install directly after building it
		return 0
