import edit_distance as ed


def cal_distance(label_list, pre_list):
    y = ed.SequenceMatcher(a=label_list, b=pre_list)
    yy = y.get_opcodes()
    insert = 0
    delete = 0
    replace = 0
    for item in yy:
        if item[0] == 'insert':
            insert += item[-1]-item[-2]
        if item[0] == 'delete':
            delete += item[2]-item[1]
        if item[0] == 'replace':
            replace += item[-1]-item[-2]
    distance = insert + delete + replace

    return distance, (delete, replace, insert)
