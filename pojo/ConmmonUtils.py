import hashlib
import uuid


def generate_unique_id(data1, data2):
    # 合并两个数据
    namespace = uuid.NAMESPACE_DNS
    unique_str = data1 + data2

    # 使用 uuid5 生成 UUID
    generated_uuid = uuid.uuid5(namespace, unique_str)

    # 转换为字符串
    uuid_str = str(generated_uuid).replace("-", "")

    return uuid_str