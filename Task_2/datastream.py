import comparator

class Processor:
    def __init__(self, cmp = comparator.HttpComparator()):
        self.cmp = cmp

    def run(self, gen):
        for (a, b) in gen:
            res = None
            try:
                res = self.cmp.equals(a, b)
            except:
                res = None

            try:
                yield (a, b, res)
            except GeneratorExit as e:
                return

class DataProvider:
    def get_file_stream(self, filename):
        return open(filename, "r")

class DataGenerator:
    def __init__(self, data_provider = DataProvider()):
        self.data_provider = DataProvider()

    def file_zip(self, file_a, file_b):
        with self.data_provider.get_file_stream(file_a) as stream_a:
            with self.data_provider.get_file_stream(file_b) as stream_b:
                for (a,b) in zip(stream_a, stream_b):
                    a = a.strip()
                    b = b.strip()
                    try:
                        yield (a,b)
                    except GeneratorExit as e:
                        return

    def file_product(self, file_a, file_b):
        with self.data_provider.get_file_stream(file_a) as stream_a:
            for a in stream_a:
                a = a.strip()

                with self.data_provider.get_file_stream(file_b) as stream_b:
                    for b in stream_b:
                        b = b.strip()
                        try:
                            yield (a,b)
                        except GeneratorExit as e:
                            return