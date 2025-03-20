import hashlib
import uuid


def generate_unique_id(data1, data2):
    # 合并两个数据

    combined_data  = data1 + data2
    unique_id = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()


    return unique_id