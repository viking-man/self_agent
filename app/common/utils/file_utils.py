import os
import logging
from app.common.error import *


def delete_file(file_path):
    try:
        # 尝试删除文件
        os.remove(file_path)
        logging.info(f"文件 {file_path} 删除成功")
    except FileNotFoundError:
        # 如果文件不存在，打印错误消息
        logging.error(f"文件 {file_path} 不存在")
        return False
    except Exception as e:
        # 如果出现其他异常，打印异常信息
        logging.error(f"删除文件 {file_path} 时出现异常: {e}")
        raise BizException(f"删除文件 {file_path} 时出现异常: {e}")
    return True
