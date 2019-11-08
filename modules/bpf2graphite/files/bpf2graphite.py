#!/usr/bin/env python3
import subprocess
import re
import socket
import select
import threading
import queue
import time
import os

class BPFParse():
    """ spawns the binary and parses contents sending to an sqs queue for later processing"""
    def __init__(self, pattern, bpfpath, metric):
        self.pattern = pattern
        self.hostname = socket.gethostname()
        self.bpfpath = bpfpath
        self.metric = metric

    def _calcvalue(self,bucket):
        """some results come back in thousands. these come back as strings with 'valK' e.g. '1K'.
        these need to be parsed out for graphite"""
        if 'K' in bucket:
            bucket = int(bucket.split('K')[0]) * 1000
        return bucket

    def _runtrace(self):
        """run bpftrace as a subprocess"""
        popen = subprocess.Popen(self.bpfpath, stdout=subprocess.PIPE)
        sel = select.poll()
        sel.register(popen.stdout,select.POLLIN)
        return (sel, popen)

    def go(self):
        """poll bpftrace for results. parse and send to queue"""
        (sel, popen) = self._runtrace()
        # when bpftrace fails we dont want to chew cpu cycles and
        # instead restart bpftrace and continue collecting metrics
        while True:
            if sel.poll(1):
                line = popen.stdout.readline()
                if not line.decode():
                    print('bpftrace has stopped sending data. restarting it in 5s')
                    time.sleep(5)
                    (sel, popen) = self._runtrace()
                for (bucket, value) in re.findall(self.pattern, line.decode()):
                    # bucket value can be in the thousands. we need to parse it
                    bucketvalue = self._calcvalue(bucket)
                    # put values onto queue
                    q.put('%s.%s.%s %s %s' % (self.hostname, self.metric, bucketvalue, float(value), int(time.time())))

def send_msg(message):
    """ send the message on to graphite. for python3
    must be a bytes-like object"""
    sock = socket.socket()
    try:
        print(message)
        sock.connect((os.environ.get("BPF2GRAPHITE_SERVER"), int(os.environ.get("BPF2GRAPHITE_PORT"))))
        sock.sendall(message.encode())
        sock.close()
    except Exception as e:
        print(e)

def worker():
    """take messages from the queue and ship them to graphite. executes on 15second intervals"""
    metrics = []
    while not q.empty():
        metrics.append(q.get())
    if metrics:
        message = '\n'.join(metrics) + '\n'
        send_msg(message)
    t = threading.Timer(15, worker)
    t.start()

if __name__ == '__main__':
    # start worker thread
    q = queue.Queue()
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    # start bpftrace and parse output, puts output onto worker thread
    cpu_latency = BPFParse(re.compile(r'\[([0-9K]{1,}).*\s([0-9]{1,})'), './cpu_latency.bt', 'cpu-lat')
    cpu_latency.go()
        
