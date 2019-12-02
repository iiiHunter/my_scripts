#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@project: new_db_process
@author: iiihunter@JinGroup
@file: test.py
@time: 18-12-10 下午9:09
@email: hesuozhang@gmail.com
'''


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


def B2Q(uchar):
    """半角转全角"""
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7e:
        # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020:
        # 除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return chr(inside_code)


def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:
        # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def stringQ2B(ustring):
    # 把字符串全角转半角
    return "".join([Q2B(uchar) for uchar in ustring])


def stringB2Q(ustring):
    # 把字符串半角转全角
    # print ustring
    return "".join([B2Q(uchar) for uchar in ustring])


if __name__ == "__main__":
    # test uniform
    #
    ustring = u'中国 人名ａ高频Ａ&(0'
    # ustring = stringQ2B(ustring)
    # print(ustring)
    # for char in ustring:
    #     print(is_other(char))
    a = '{'
    print(a)
    print(B2Q(a))
