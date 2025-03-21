import base64
import os


def file_to_base64(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")

    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")
    return encoded_string
def base64_to_file(base64_str, output_path):
    """将 Base64 编码的数据转换回文件"""
    try:
        with open(output_path, "wb") as file:
            file.write(base64.b64decode(base64_str))
        print(f"文件已成功保存到: {output_path}")
    except Exception as e:
        print(f"文件保存失败: {e}")