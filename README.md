# bpf2graphite

Parse BPFTrace output and ship values to graphite

# Features

* written in python which spawns bpftrace and parses output in realtime without writing to disk
* Systemd service to start bpf2graphite
* Sends data to graphite by opening a socket to the server
* Sends data to graphite in 15second increments
* Can specify graphite server to send output to via Environment Variables
* Takes care of high values (e.g. 1K) before sending to Graphite
* Buffers input via an Queue before sending to Graphite

# Directory Structure
.
├── README.md
├── local.pp
└── modules
    └── bpf2graphite
        ├── CHANGELOG.md
        ├── files
        │   ├── bpf2graphite.py
        │   └── cpu_latency.bt
        ├── manifests
        │   └── init.pp
        ├── metadata.json
        └── templates
            └── bpf2graphite.service.erb


# Installation
BPF2Graphite can easily be installed with the puppet module provided within this repository.

To install locally with puppet - 

# local.pp
```
class { 'BPF2Graphite': }

puppet apply --modulepath modules/ local.pp
```

An example:
```
puppet apply --modulepath modules/ local.pp

Notice: Compiled catalog for tuxgrid.com in environment production in 0.76 seconds
Notice: /Stage[main]/Bpf2graphite/File[/opt/bpf2graphite]/ensure: created
Notice: /Stage[main]/Bpf2graphite/File[/opt/bpf2graphite/bpf2graphite.py]/ensure: defined content as '{md5}65a38c1741c946e60db8bc7ccec7f7c8'
Notice: /Stage[main]/Bpf2graphite/File[/opt/bpf2graphite/cpu_latency.bt]/ensure: defined content as '{md5}f41db42e8518738e316f48780126eed9'
Notice: /Stage[main]/Bpf2graphite/File[/etc/systemd/system/bpf2graphite.service]/ensure: defined content as '{md5}e30509f05abaad418c4065ef7b01372d'
Notice: /Stage[main]/Bpf2graphite/Service[bpf2graphite]/ensure: ensure changed 'stopped' to 'running'
Notice: Applied catalog in 0.63 seconds
```

The following will appear in process tree - 
```
├─python3─┬─bpftrace
        └─{python3}

```

# local (manual) run
To run locally -
1. ensure bpftrace is installed
2. ensure cpu_latency.bt is in same directory as the python script
4. set graphite environment variables. default will return an error when tries to ship to graphite
	export BPF2GRAPHITE_SERVER=localhost
	export BPF2GRAPHITE_PORT=2003
5. run python script from the same directory as cpu_latency.bt. requires python3.

# Functions & Classes

## BPFParse (class) - Spawns bpftrace and sends the contents to an sqs queue for later processing
_calcvalue - Takes care of high values before sending to Graphite
_runtrace - Starts bpftrace in a subprocess
go - parses results and ships to queue

## send_msg - sends the messages to graphite
## worker - gets messages from queue, batches up to send all messages in queue in a single operation. runs itself every 15s

# Testing

No working tests have been provided with this example due to time constraints.
It would be sensible to include mocking and unit tests at a later date

A sample graphite server can be started with the following docker commands for testing purposes
```
docker run -d --name graphite --restart=always -p 80:80 -p 2003-2004:2003-2004 -p 2023-2024:2023-2024 -p 8125:8125/udp -p 8126:8126 graphiteapp/graphite-statsd
```

# Known Issues

* Does not take input from a configuration file to allow different bpftrace files to be parsed [FEATURE]
* If bpftrace crashes will not respawn bpftrace and result in a script not sending input to graphite. script fails with 100% core use [BLOCKER TO PRODUCTION USE]
* has no command line args. may come in a later version. [FEATURE]

# Example Output (Graphite not running)

Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.4 1.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.8 1.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 0.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 1.0 1572824522
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.8 1.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.256 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.512 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.1000 0.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.2000 1.0 1572824523
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.4 1.0 1572824524
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.2 2.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.4 4.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.8 1.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 0.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 1.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.256 1.0 1572824527
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 1.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.256 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.512 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.1000 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.2000 0.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.4000 1.0 1572824528
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.8 1.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 0.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 1.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.256 1.0 1572824529
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.16 1.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.32 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.64 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.128 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.256 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.512 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.1000 0.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.2000 1.0 1572824530
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: tuxgrid.com.cpu-lat.4 1.0 1572824531
Nov  3 23:42:57 tuxgrid bpf2graphite.py[12021]: [Errno 111] Connection refused


