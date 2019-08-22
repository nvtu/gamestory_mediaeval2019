from multiprocessing import Process
import multiprocessing


class MultiProcessTask:

    def __init__(self, params, func):
        self.params = params
        self.func = func


    def __run_task(self, params, func):
        for p in params:
            func(p) 


    def run_multiprocess(self):
        n_proc = multiprocessing.cpu_count() - 1
        n_task_per_proc = self.params.__len__() // n_proc + 1
        proc = []
        for i in range(n_proc):
            _param = self.params[i * n_task_per_proc : min((i + 1) * n_task_per_proc, self.params.__len__())]
            proc.append(Process(target=self.__run_task, args=(_param, self.func, )))
            proc[-1].start()
        for task in proc:
            task.join()
