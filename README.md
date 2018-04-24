# MoneroMiner

## deepMiner(https://github.com/deepwn/deepMiner)

用于转化WebSocket流量与PoolSocket(TCP)流量的中间件

参见：

Coinhive挖矿脚本分析与Pool改造自建(一) (http://www.freebuf.com/column/151316.html)

Coinhive挖矿脚本分析与Pool改造自建(二) (http://www.freebuf.com/column/151376.html)

## xmr-proxy(https://github.com/Atrides/xmr-proxy)

Stratum Proxy for Monero-pools (RPCv2) using asynchronous networking written in Python Twisted.

## xmr-node-proxy(https://github.com/Snipa22/xmr-node-proxy/blob/master/proxy.js)

Stratum Proxy for Monero-pools written in Node.js.

## Node Open Mining Portal(https://github.com/zone117x/node-open-mining-portal)

This portal is an extremely efficient, highly scalable, all-in-one, easy to setup cryptocurrency mining pool written entirely in Node.js. 

## CoinHive Stratum Mining Proxy(https://github.com/x25/coinhive-stratum-mining-proxy)

A proof of concept of web mining using CoinHive's JavaScript Mining library. The proxy acts like coin hive to connect to a mining pool. Should work with any monero pool based on the Stratum Mining Protocol. 

## XMR-Stak(https://github.com/fireice-uk/xmr-stak)

优化过的Cpu/GPU Miner

### minethd.cpp:

void minethd::work_main()

      //在最早的1.6s内全速36ms,然后降速到60ms(sleep)，可以解决2GHz CPU的占用，维持在40%左右
      
			int mseconds = 36+int(result.iNonce/16);
      
			if(mseconds>60)
      
			    mseconds=60;
          
			std::this_thread::yield();
      
			std::this_thread::sleep_for(std::chrono::milliseconds(mseconds));
      
			std::this_thread::yield();
      
### executor.cpp:

void executor::eval_pool_choice()

  	//bool dev_time = is_dev_time();
  
  	//不要donate
  
	bool dev_time = false;
