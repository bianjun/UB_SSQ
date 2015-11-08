import sqlite3
import heapq
import matplotlib.pyplot as plt
import numpy as sp
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

def SpeBlueBallFit(blue_ball_no):
    ssq_db = cls_ssq.SsqSqlite3Db()
    fit_data_after_spe_bb = ssq_db.ExecuteSql('select rowid, ssqbb from lottery_ssq where '\
                                       'rowid in (select rowid + 1 from lottery_ssq where ssqbb = {bb_no})'.format(bb_no = blue_ball_no))
    ssq_db.close()
    #print(fit_data_after_spe_bb)
    x = [x[0] for x in fit_data_after_spe_bb]
    #x = [1 for x in fit_data_after_spe_bb]
    y = [y[1] for y in fit_data_after_spe_bb]

    plt.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体  
    plt.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题

    plt.scatter(x, y)
    plt.title(u'蓝号：{} 下一次双色球的拟化曲线'.format(blue_ball_no))
    plt.xlabel(u'期数')
    plt.ylabel(u'蓝号')
    plt.autoscale(tight=True)
    plt.grid()
    

    fp1, residuals, rank, sv, rcond = sp.polyfit(x, y, 40, full=True)
    #print(fp1)
    f1 = sp.poly1d(fp1)
    next_bb = x[-1] + 1
    print('预测{next_bb}号为：{num}'.format(next_bb = next_bb, num = f1(1872)))
    fx = sp.linspace(x[0], x[-1])
    plt.plot(fx, f1(fx), linewidth = 1)
    plt.legend(["d = %i" % f1.order], loc = 'upper left')

    plt.show()

def SpeCurBlueBallFit():
    ssq_db = cls_ssq.SsqSqlite3Db()
    latest_bb = ssq_db.ExecuteSql('select max(ssqid),ssqbb from lottery_ssq')
    ssq_db.close()

    #print(latest_bb[0][1])
    SpeBlueBallFit(latest_bb[0][1])

if __name__ == '__main__':
    WhichBlueBallIsTheBestInHistory()
    SpeCurBlueBallFit()
    #SpeBlueBallFit(10)
    #SpeBlueBallFit(4)
    #SpeBlueBallFit(6)
    
