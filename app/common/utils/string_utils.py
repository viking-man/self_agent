import re
from opencc import OpenCC

from pypinyin import pinyin, Style

def chinese_to_pinyin(text):
    # 使用 pinyin() 函数将汉字转换为拼音
    pinyin_result = pinyin(text, style=Style.NORMAL)
    # 将拼音列表连接为字符串
    result_str = ' '.join([item[0] for item in pinyin_result])
    return result_str

def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(pattern.search(text))


def convert_simple2traditional(text):
    if contains_chinese(text):
        # 创建一个 OpenCC 实例，用于简繁体中文转换
        converter = OpenCC('s2t')  # 简体中文(s) 转繁体中文(t)
        # 示例字符串，这里假设是要匹配的简体中文字符串
        # 将简体中文转换为繁体中文
        traditional_chinese_text = converter.convert(text)
        return traditional_chinese_text
    else:
        return text


if __name__ == '__main__':
    # 示例
    text = "十七岁"
    if contains_chinese(text):
        print("包含中文字符")
    else:
        print("不包含中文字符")

    traditional = convert_simple2traditional(text)
    # 输出转换结果
    print("繁体中文:", traditional)
