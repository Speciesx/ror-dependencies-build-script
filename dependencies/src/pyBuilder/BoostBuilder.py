from pyBuilder import *

class BoostBuilder(BuildTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/boost_*.zip')
		
	def configure(self):
		return self.execute(r"""
cd boost_*
echo "bootstrapping boost ..."
call bootstrap.bat
call:checkReturnValue
""")
			
	def build(self):
		global PLATFORMS, CONFIGURATIONS
		cmd = r"""
cd boost_*
"""
		if 'x86' in PLATFORMS:
			if 'Release' in CONFIGURATIONS:
				cmd += r"""
echo "building boost 32 bits RELEASE ..."
bjam -j%(maxcpu)d --toolset=msvc-14.0 address-model=32 variant=release link=static threading=multi runtime-link=shared --build-type=minimal --stagedir=x86
call:checkReturnValue
"""		
			if 'Debug' in CONFIGURATIONS:
				cmd += r"""
echo "building boost 32 bits DEBUG ..."
bjam -j%(maxcpu)d --toolset=msvc-14.0 address-model=32 variant=debug inlining=off debug-symbols=on link=static threading=multi runtime-link=shared --build-type=minimal --stagedir=x86
call:checkReturnValue
"""		
	
		if 'x64' in PLATFORMS:
			if 'Release' in CONFIGURATIONS:
				cmd += r"""
echo "building boost 64 bits RELEASE ..."
bjam -j%(maxcpu)d --toolset=msvc-14.0 address-model=64 variant=release link=static threading=multi runtime-link=shared --build-type=minimal --stagedir=x64
call:checkReturnValue
"""		

			if 'Debug' in CONFIGURATIONS:
				cmd += r"""
echo "building boost 64 bits DEBUG ..."
bjam -j%(maxcpu)d --toolset=msvc-14.0 address-model=64 variant=debug inlining=off debug-symbols=on link=static threading=multi runtime-link=shared --build-type=minimal --stagedir=x64
call:checkReturnValue
"""		
		return self.execute(cmd)
			
	def install(self):
		global PLATFORMS, CONFIGURATIONS
		dir = self.getFirstFolder()
		res = 0
		self.arch = 'x86'
		if 'x86' in PLATFORMS:
			res |= self.installIncludes(dir+'/boost', True, 'boost')
			res |= self.installLibs(dir+'/%(arch)s/lib/*.lib')
		if 'x64' in PLATFORMS:
			self.arch = 'x64'
			res |= self.installIncludes(dir+'/boost', True, 'boost')
			res |= self.installLibs(dir+'/%(arch)s/lib/*.lib')
		return res