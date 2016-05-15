import sys
import os
import time
import os.path
import zipfile
import subprocess
import shutil 
import glob
import datetime

MAXCPU=4
CMAKE_PATH=os.environ['ProgramFiles(x86)']+"\\CMake"
DEV_ENV_BATCH=os.environ['ProgramFiles(x86)']+"\\Microsoft Visual Studio 14.0\\VC\\vcvarsall.bat"
DEBUG=False
CONTINUE_ON_ERROR=False
CONFIGURATIONS=[]
# return value convention: 0 : success, != 0 : failure

from pyBuilder import *
from WTCW import *

class BuildTarget:
	path     = ''
	target   = ''
	arch     = 'x86'
	platform = 'win32'
	generator = ''
	configuration = ''
	
	def mkd(self, dirs):
		path = os.path.abspath(self.path + '/' + dirs)
		print 'mkdir ' + path
		return os.system('mkdir ' + path)
		
	def clean(self):
		if os.path.isdir(self.path):
			return self.rm_rf(self.path)
		return 0

	def unzip(self, source, path = ''):
		if path == '':
			path = self.path
		else:
			path = glob.glob(path)[0]
			
		zipfiles = glob.glob(os.path.join(ROOT,source))
		if len(zipfiles) == 0:
			print "no zip files found that match in path: ", source, os.path.join(ROOT,source)
			return 1
		for f in zipfiles:
			print "unpacking ",f," to ", path, " ..."
			try:
				zip = zipfile.ZipFile(f)
				zip.extractall(path)
			except Exception as e:
				print "exception while unzipping: ", e
				return 1
		return 0

	def rm_rf(self, d):
		print "rmdir: ", d
		return os.system('rd /s /q ' + d)
		
	def initPaths(self):
		path = self.__class__.__name__.replace('Builder', '')
		self.target = path
		self.path = os.path.abspath(ROOT+'/'+path)
	
	def _installBase(self, src, dst, type, required, dstDir):
		# first: fill possible args
		src = self._fillArgs(src)
		dst = self._fillArgs(dst)
		# then normalize the whole paths
		srcPath = os.path.abspath(self.path+'/'+src)
		if type == 'includes':
			dstPath = os.path.abspath(DEPS+'/'+type+'/'+ self.arch +'/'+dst+'/'+dstDir)
		else:
			dstPath = os.path.abspath(DEPS+'/'+type+'/'+ self.arch +'/'+dst+'/'+self.configuration+'/'+dstDir)
		# create the target directory if it is not existing
		if not os.path.isdir(dstPath):
			os.makedirs(dstPath)
		# invoke the system
		print srcPath, ' --> ', dstPath
		# map xcopy result codes to ours, CHANGE: no files found to copy = no error
		#0 Files were copied without error. 
		#1 No files were found to copy. 
		#2 The user pressed CTRL+C to terminate xcopy. 
		#4 Initialization error occurred. There is not enough memory or disk space, or you entered an invalid drive name or invalid syntax on the command line. 
		#5 Disk write error occurred. 
		
		noFilesFound = False
		globFiles = glob.glob(srcPath)
		if len(globFiles) == 0 and not os.path.isfile(srcPath) and not os.path.isdir(srcPath):
			print "{rg}XCOPY WARNING: no files found! for path %s" % srcPath
			noFilesFound = True
		
		xcmd = "xcopy /S /Y %s %s" % (srcPath, dstPath)
		res = os.system (xcmd)
		if DEBUG:
			print "XCOPY CMD: ", xcmd
			if res  == 0:
				print "{G}XCOPY RESULT: ", res
			elif res  != 0 and not required:
				print "{RG}XCOPY RESULT: ", res
			else:
				print "{R}XCOPY RESULT: ", res
		
		if not required:
			return 0
		if noFilesFound:
			return 1
		return res
	
	def installIncludes(self, src, required=True, dstDir = ''):
		return self._installBase(src, self.target, 'includes', required, dstDir)

	def installLibs(self, src, required=True, dstDir = ''):
		return self._installBase(src, self.target, 'libs', required, dstDir)

	def installBinaries(self, src, required=True, dstDir = ''):
		return self._installBase(src, self.target, 'bin', required, dstDir)

	def banner(self, txt, col=''):
		print col+'#'*80
		print col+'#'*10,txt
		print col+'#'*80

	def getFirstFolder(self):
		for f in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, f)):
				return f
		return ''
		
	def _fillArgs(self, str):
		return str % self._getArgs()
		
	def _getArgs(self):
		args = {}
		args['path']      = self.path
		args['rootdir']   = ROOT
		args['depsdir']   = DEPS
		args['depsdir_cmake']   = DEPS.replace('\\', '/')
		args['arch']      = self.arch
		args['arch_bits'] = 32
		if self.arch == 'x64':
			args['arch_bits'] = 64
		args['generator'] = self.generator
		args['platform']  = self.platform
		args['target']    = self.target
		# restricted configurations to Release and Debug
		cr = self.configuration
		if   cr == 'RelWithDebInfo' or cr == 'MinSizeRel': cr = 'Release'
		args['configuration_restricted'] = cr
		args['configuration'] = self.configuration
		args['debug_d'] = ''
		if self.configuration == 'Debug':
			args['debug_d'] = '_d'
		
		args['conf']      = self.configuration
		args['maxcpu']    = MAXCPU
		args['cmakedir']  = CMAKE_PATH
		args['devenv_batch'] = DEV_ENV_BATCH
		args['vswarninglevel'] = 0 # no warnings
		if DEBUG:
			args['vsverbosity'] = 'm' # q[uiet], m[inimal], n[ormal], d[etailed], dia[gnostic]
		else:
			args['vsverbosity'] = 'q'
			
		
		return args
			
	def execute(self, cmd):
		cmdFile = self.path+'/exec.cmd'
		
		args = self._getArgs()
		f = open(cmdFile, "w")
		if DEBUG:
			f.write("@echo on\n")
		else:
			f.write("@echo off\n")
		f.write(r"""
:: AUTO-GENERATED, do not modify\n")
:: setup PATH
SET PATH=%%PATH%%;%(rootdir)s;%(cmakedir)s\\bin;

:: Load compilation environment
call "%(devenv_batch)s"
""" % args)

		if DEBUG:
			f.write("@echo on\n")
		
		f.write(r"""
:: change the directory
cd %(path)s
:: the actual command we want to execute
""" % args)
		
		# replace magic in commands
		command = self._fillArgs(cmd)

		f.write(command+"\n")
		f.write(r"""
:: DONE
cd %(rootdir)s

GOTO PYTHONBUILDEREND
:::: FUNCTIONS BELOW
:checkReturnValue
@IF "%%ERRORLEVEL%%"=="0" (
	@echo ### everything looks good, continuing ...
	@GOTO:EOF
) ELSE (
	@echo ### error level is set to %%errorlevel%%
	@echo ### something failed, exiting
	@cd %(rootdir)s
	@exit %%ERRORLEVEL%%
)
@GOTO:EOF
:PYTHONBUILDEREND
:: END""" % args)
		f.close()
		
		proc = subprocess.Popen('cmd /s /c '+cmdFile,
							   shell=True)
							   #stdin=subprocess.PIPE,
							   #stdout=subprocess.PIPE,
							   #stderr=subprocess.STDOUT,
							   #)
		res = proc.wait()
		"""
		res = None
		while proc.poll():
			line = proc.stdout.readline()
			print '...'+line.rstrip()
			#print '{r}%s|{x}%s' % (self.target, line)
			res = proc.poll()
			if line == '' and res != None:
				break
		"""
		
		#res = subprocess.call(cmdFile, shell=True)
		if DEBUG:
			if res  == 0:
				print "{G}EXECUTE RESULT: ", res
			else:
				print "{R}EXECUTE RESULT: ", res
			
		#if res != 0:
		#	raise Exception("command execution failed with error code ", res)
		if not DEBUG:
			os.unlink(cmdFile)
		return res
	
	def configure(self):
		return False

	def extract(self):
		return False

	def build(self):
		return False

	def install(self):
		return False
		
	def buildAll(self):
		res = 0
		if self.clean() != 0:
			self.banner("CLEAN FAILED", '{ri}')
			if CONTINUE_ON_ERROR:
				res = 1
			else:
				return 1

		if self.extract() != 0:
			self.banner("EXTRACT FAILED", '{ri}')
			if CONTINUE_ON_ERROR:
				res = 1
			else:
				return 1
				
		if self.configure() != 0:
			self.banner("CONFIGURE FAILED", '{ri}')
			if CONTINUE_ON_ERROR:
				res = 1
			else:
				return 1

		if self.build() != 0:
			self.banner("BUILD FAILED", '{ri}')
			if CONTINUE_ON_ERROR:
				res = 1
			else:
				return 1

		if self.install() != 0:
			self.banner("INSTALL FAILED", '{ri}')
			if CONTINUE_ON_ERROR:
				res = 1
			else:
				return 1

		return res
		
class BuildCMakeTarget(BuildTarget):
	def buildAll(self):
		archs = {}
		
		if 'x86' in PLATFORMS:
			archs['x86'] = ['x86', 'win32', '"Visual Studio 14"']
		if 'x64' in PLATFORMS:
			archs['x64'] = ['x64', 'x64',   '"Visual Studio 14 Win64"']

		if self.clean() != 0:
			self.banner("CLEAN FAILED: " + self.target, '{r}')
			return 1
		
		if self.extract() != 0:
			self.banner("EXTRACTION FAILED: " + self.target, '{r}')
			return 1
		res = 0
		sarchall = StopWatch("build all archs " + self.target)
		for arch in archs:
			self.arch      = archs[arch][0]
			self.platform  = archs[arch][1]
			self.generator = archs[arch][2]
			
			for configuration in CONFIGURATIONS:
				self.configuration = configuration
				
				self.banner(self.target + ' / ' + configuration + ' / ' + self.arch + ' / ' + self.platform  + ' / ' + self.generator, '{gb}')

				if self.configure() != 0:
					self.banner("CONFIGURE FAILED", '{ri}')
					if CONTINUE_ON_ERROR:
						res = 1
						continue
					else:
						return 1
						
				if self.build() != 0:
					self.banner("BUILD FAILED", '{RrI}')
					if CONTINUE_ON_ERROR:
						res = 1
						continue
					else:
						return 1
				
				if self.install() != 0:
					self.banner("INSTALL FAILED", '{ri}')
					if CONTINUE_ON_ERROR:
						res = 1
						continue
					else:
						return 1
				
		sarchall.report()
		return res

class StopWatch():
	def __init__(self, txt):
		self.start = time.clock()
		self.txt = txt
	def report(self):
		self.end = time.clock()
		print '{i}%s - {rgb} %s' % (self.txt, str(datetime.timedelta(seconds=self.end - self.start)))
		
def check_requirements():
	if sys.version_info[0] != 2:
		print "this script will only work in python 2"
		return False
	if not os.path.isdir(CMAKE_PATH):
		print "cmake not found in "+CMAKE_PATH
		print "please install CMake 2.8 to " + CMAKE_PATH
		return False
	if not os.path.isfile(DEV_ENV_BATCH):
		print "Visual Studio 2015 not found. Please install"
		return False
	return True

def banner2(txt, col=''):
	print col+chr(201)+chr(205)*80+chr(187)
	print col+chr(186)+txt.center(80)+chr(186)
	print col+chr(200)+chr(205)*80+chr(188)

def run(root, deps, configurations, platforms):
	sys.stdout = WTCW(sys.stdout)
	if not check_requirements():
		return
		
	# store config in global
	globals()['ROOT'] = root
	globals()['DEPS'] = deps
	globals()['CONFIGURATIONS'] = configurations
	globals()['PLATFORMS'] = platforms

	builders = {}
	for b in glob.glob(os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__ ))),'*Builder.py')):
		name = os.path.basename(b).split('.')[0]
		builders[name] = __import__(name, globals(), locals(), [], -1)
		# copy globals
		builders[name].__dict__.update(globals())
	
	buildOrder = """
# standalone libs first
  WxWidgetsBuilder 
  MoFileReaderBuilder
  SocketWBuilder
  AngelScriptBuilder
  OISBuilder
  CurlBuilder
  OpenALSoftBuilder
  OgreBuilder
# then the libs depending on ogre
  PagedGeometryBuilder
  CaelumBuilder
  MyGUIBuilder
""".split("\n")

	# build everything
	sw = StopWatch("time since startup ")
	res = 0
	for b in buildOrder:
		b = b.strip()
		if len(b) == 0 or b[0] == '#':
			continue
		banner2(b.replace('Builder',''), '{Ib}')
		instance = getattr(builders[b],b)
		res = instance().buildAll()
		if res != 0:
			if CONTINUE_ON_ERROR:
				print ">>> A BUILDER FAILED, CONTINUING <<<"
				res = 1
				continue
			else:
				print ">>> A BUILDER FAILED, EXITING <<<"
				sw.report()
				return 1
	sw.report()
	return res
