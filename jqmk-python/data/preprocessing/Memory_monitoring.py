import psutil
import time
import datetime

def format_bytes(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

def monitor_memory(interval=1, log_file="memory_log.txt", stop_time="00:04:00"):
    print(f"开始实时监测内存，直到 {stop_time}\n")

    with open(log_file, "a", encoding="utf-8") as f:
        header = "时间\t\t\t总内存\t已使用\t剩余\t缓存\t使用率\n"
        f.write(header)
        print(header.strip())

        try:
            while True:
                now = datetime.datetime.now()
                now_str = now.strftime("%H:%M:%S")

                if now_str >= stop_time:
                    print(f"\n达到设定停止时间 {stop_time}，监测自动结束。")
                    break

                mem = psutil.virtual_memory()

                total = format_bytes(mem.total)
                used = format_bytes(mem.used)
                available = format_bytes(mem.available)
                cached = format_bytes(getattr(mem, 'cached', 0))
                percent = f"{mem.percent:.1f}%"

                line = (f"{now.strftime('%Y-%m-%d %H:%M:%S')}\t{total}\t{used}\t{available}\t{cached}\t{percent}")
                print(line)
                f.write(line + "\n")
                f.flush()
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n监测被用户中断，数据已写入。")

if __name__ == "__main__":
    monitor_memory()
