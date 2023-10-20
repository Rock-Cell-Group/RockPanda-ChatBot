import time

# Define a decorator function to calculate the execution time of another function.
def calculate_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs) # Call the original function.
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} 執行時間：{execution_time}秒")
        return result
    return wrapper