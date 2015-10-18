import sqlite3
import heapq
import Cls_SsqSqlite3Db as cls_ssq
import SsqBlueballRuleController as bbrc

def WhichBlueBallIsTheBestInHistory():
    ssq_db = cls_ssq.SsqSqlite3Db()

    the_latest3_bb = ssq_db.ExecuteSql('SELECT ssqbb FROM lottery_ssq ORDER BY ssqid DESC LIMIT 3')

    after_cur_bb = ssq_db.ExecuteSql('SELECT follow_there FROM blueball_rule WHERE bb_id = {bb_id}'.format(bb_id = the_latest3_bb[0][0]))[0][0]
    after_last_one = ssq_db.ExecuteSql('SELECT follow_there FROM blueball_rule WHERE bb_id = {bb_id}'.format(bb_id = the_latest3_bb[1][0]))[0][0]
    after_last_two = ssq_db.ExecuteSql('SELECT follow_there FROM blueball_rule WHERE bb_id = {bb_id}'.format(bb_id = the_latest3_bb[2][0]))[0][0]

    after_cur_bb = eval('{}'.format(after_cur_bb))[0]
    after_last_one = eval('{}'.format(after_last_one))[1]
    after_last_two = eval('{}'.format(after_last_two))[2]

    #print(after_cur_bb)
    #print(after_last_one)
    #print(after_last_two)

    #综合三个结果选出最多的三个
    total_in_history = {}
    for bb in range(1, 17, 1):
        total_in_history[bb] = after_cur_bb.get(bb, 0) + after_last_one.get(bb, 0) + after_last_two.get(bb, 0)

    #print(total_in_history)
    top3_in_history = heapq.nlargest(3, zip(total_in_history.values(), total_in_history.keys()))

    print('从最近三次出现的蓝球及其规则来看，解析来最有可能出现的是:')
    for data in top3_in_history:
        print(data[1], data[0], sep = ':')
    
    ssq_db.close()

if __name__ == '__main__':
    WhichBlueBallIsTheBestInHistory()
    
