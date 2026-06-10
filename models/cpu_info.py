class CpuInfo:
    def __init__(self,model,usage,frequency,cores,threads,average_usage=None,peak_usage=None,temperature=None):
        self.model = model
        self.usage = usage
        self.frequency = frequency
        self.cores = cores
        self.threads = threads

        self.average_usage = average_usage
        self.peak_usage = peak_usage
        self.temperature = temperature