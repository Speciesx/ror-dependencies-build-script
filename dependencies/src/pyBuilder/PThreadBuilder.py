from pyBuilder import *

class PThreadBuilder(BuildCMakeTarget):
	def __init__(self):
		self.initPaths()
		
	def extract(self):
		return self.unzip('files/pthreads*.zip')
		
	def configure(self):
		dir = self.getFirstFolder()
		self.mkd(dir+'/build_'+self.arch)
		return self.execute(r"""
cd %(path)s\pthreads-win32*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue

cmake .. -G %(generator)s ..
 @call:checkReturnValue
""")

	def build(self):
		return self.execute(r"""
cd %(path)s\pthreads-win32*
@call:checkReturnValue

cd build_%(arch)s
@call:checkReturnValue	

msbuild pthreads-win32.sln /t:rebuild /p:Configuration=%(configuration)s /p:Platform=%(platform)s /verbosity:%(vsverbosity)s /nologo /maxcpucount:%(maxcpu)d
@call:checkReturnValue
""")

	def install(self):
		dir  = self.getFirstFolder()
		res  = self.installIncludes(dir+'/pthreads-win32/pthread.h')
		res |= self.installIncludes(dir+'/pthreads-win32/semaphore.h')
		res |= self.installIncludes(dir+'/pthreads-win32/sched.h')
		res |= self.installLibs(dir+'/build_%(arch)s/%(conf)s/pthreadsVC2.lib')
		res |= self.installBinaries(dir+'/build_%(arch)s/%(conf)s/pthreadsVC2.dll')
		return 0