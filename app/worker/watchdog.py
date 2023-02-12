# Import the queue, threading and time modules
import os
import queue
import threading
import multiprocessing
import time

from app import constants
from app.constants import Status, Paths
from app import database
from . import workerServices


should_run = False
watchdog_thread_id = None
def start_watchdog():
    global should_run, watchdog_thread_id

    threads = threading.enumerate()

    workerQueue = queue.Queue()
    threads = []

    # Get the jobs from the database and put them in the queue
    jobs = get_jobs_from_database()
    for job in jobs:
        workerQueue.put(job)
        database.updateItemStatus(job['id'], "pending")

    # Create a lock object to synchronize the access to the queue and the threads list
    lock = threading.Lock()

    should_run = True

    # Create and start the watchdog thread and pass the queue, the threads, the lock and the timeout as arguments
    watchdog_thread = threading.Thread(target=watchdog, name="Watchdog", daemon=True, args=(workerQueue, threads, lock, 5))
    watchdog_thread.daemon = True
    watchdog_thread.start()

    watchdog_thread_id = watchdog_thread.ident

    # watchdog_thread.join()

    print( "Watchdog started" )

def stop_watchdog():
    global should_run
    print( "Watchdog shutting down" )
    should_run = False

    # kill off any subprocess that are currently running
    active = multiprocessing.active_children()
    print( active )


def is_watchdog_running():
    global watchdog_thread_id

    threads = threading.enumerate()
    if watchdog_thread_id is None:
        return False
    return threading.Thread.ident == watchdog_thread_id


# Define a function for the watchdog thread
def watchdog(queue, threads, lock, timeout):
    global watchdog_thread_id

    thread = threading.current_thread()
    print(f"{thread.name} started at {time.ctime()}")

    # Loop forever, we never want the watchdog to stop
    while True:
        try:
            # Loop through the threads
            for t in threads:
                # Check if the thread is alive
                if not t.is_alive():
                    # Print the thread name and the status
                    print(f"{t.name} is done")
                    threads.remove(t)

            # We're only going to add now jobs if we aren't shutting down
            if should_run:
                items = database.getItemsWithStatus(Status.waiting)
                for item in items:
                    queue.put(item)
                    database.updateItemStatus(item['id'], Status.pending)

            # Check the number of items in the queue
            size = queue.qsize()

            # Print the queue size
            # print(f"There are {size} items in the queue")

            # Check if there are new jobs waiting
            if size > 0:
                # Acquire the lock
                lock.acquire()

                # We're going to start a maximum of 2 new threads
                nrThreadsRequired = min(size - len(threads), 2)
                if nrThreadsRequired > 0:
                    # Create and start new worker threads and pass the queue as an argument
                    for i in range(0, nrThreadsRequired):
                        t = threading.Thread(target=worker, name=f"Worker-{i}", args=(queue,))
                        t.start()
                        threads.append(t)
                # Release the lock
                lock.release()
            # Sleep for one second
            time.sleep(1)
        except Exception as e:
            # Print the exception
            print(e)

    # Print the thread name and end time
    print(f"{thread.name} ended at {time.ctime()}")
    print( "Watchdog thread is done" )


# Define a function to connect to the database and get the jobs
def get_jobs_from_database():

    # First lets cleanup any pending jobs from previous runs
    # if any files still in the inprogress folder,
    # move them back to the waiting folder and reset status back to waiting
    # if file not in DB then delete it
    inprogress = database.getItemsWithStatus(Status.inprogress)
    for item in inprogress:
        if item['type'] == constants.audio_type:
            id = item['id']
            if os.path.exists(f"{Paths.inprogress}/{id}.wav" ):
                print( f"Resetting job {id} back to waiting")
                os.rename(f"{Paths.inprogress}/{id}.wav", f"{Paths.waiting}/{id}.wav")
                database.updateItemStatus(id, Status.waiting)
            else:
                print( f"Removing job {id} as source file not found")
                database.deleteItem(id)

        elif item['type'] == constants.youtube_type:
            # youtube file, reset to pending
            database.updateItemStatus(item['id'], Status.waiting)

    # now delete any remaining files in the inprogress folder
    for filename in os.listdir(Paths.inprogress):
        print( f"cleaning up {filename} - not in DB!")
        os.remove(f"{Paths.inprogress}/{filename}")

    pending = database.getItemsWithStatus(Status.pending)
    waiting = database.getItemsWithStatus(Status.waiting)

    print( "Pending: " + str(len(pending)) )
    print( "Waiting: " + str(len(waiting)) )

    return pending + waiting

# Define a function for the worker thread
def worker(queue):
    # Get the current thread object
    thread = threading.current_thread()
    # Loop until the queue is empty
    while not queue.empty():
        # Get a job from the queue
        job = queue.get()
        # Print the thread name and the job
        print(f"{thread.name} is working on {job}")

        workerServices.handleTask(job)

        # Print the thread name and the job
        print(f"{thread.name} has finished {job}")
        # Indicate that the task is done
        queue.task_done()


# Create a queue to store the jobs
