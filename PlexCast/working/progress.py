import time, sys, threading

def do_task():
	time.sleep(0.1)

def start_watchers():
    for i in range(3):
        watcher = threading.Thread(target=start)
        # watcher.setDaemon(True)
        watcher.start()

def example_1(n):
	steps = n/10
	for i in range(n):
		do_task()
		if i%steps == 0:
			print '\b.',
			sys.stdout.flush()
	print '\b]  Done!',

def start():
    print 'Starting [          ]',
    print '\b'*12,
    sys.stdout.flush()
    example_1(100)


start_watchers()