# https://github.com/rapidsai/kvikio/issues/629

import cudf
import cupy
import rmm
import nvtx
import time
from io import BytesIO


class TestManager:
    def __init__(self):
        rmm.mr.set_current_device_resource(rmm.mr.CudaAsyncMemoryResource())
        cupy.random.seed(2077)
        self.file_path = "/mnt/nvme/tmp.pq"

    def write_to_file(self):
        print("Write to file")
        nrows = int(1.6 * 10**8)

        df = cudf.DataFrame({
            'a': cupy.random.rand(nrows)
        })

        df.to_parquet(
            self.file_path,
            compression=None,
            column_encoding='PLAIN',
        )

    def read_from_file(self):
        print("Read from file to device memory")
        for idx in range(1):
            with nvtx.annotate("Python read file"):
                start = time.time()
                _ = cudf.read_parquet(self.file_path)
                elapsed_time = time.time() - start
                print("{:4d} - {:.6f} [s]".format(idx, elapsed_time))

        # buf = BytesIO()
        # df.to_parquet(
        #     buf,
        #     compression=None,
        #     column_encoding='PLAIN',
        # )

        # for r in range(10):
        #     with nvtx.annotate("read host buffer"):
        #         buf.seek(0)
        #         t0 = time.time()
        #         _ = cudf.read_parquet(buf)
        #         t1 = time.time()
        #         print(f"read host buffer: {t1-t0}")


if __name__ == "__main__":
    tm = TestManager()
    # tm.write_to_file()
    tm.read_from_file()
