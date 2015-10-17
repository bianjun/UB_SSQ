import sqlite3
from abc import ABCMeta,abstractmethod
import Cls_SsqSqlite3Db as cls_ssq

class SsqBbrController(metaclass = ABCMeta):
    def __init__(self, rule_name, rule_type):
        self.db = cls_ssq.SsqSqlite3Db()
        self.rule_name = rule_name
        self.rule_type = rule_type

    @abstractmethod
    def UpdateRuleData(self):
        pass

    def UpdateRule(self):
        """如果没有就创建"""
        exist_rules = self.db.GetBlueBallRulesName()
        #print(exist_rules)
        if exist_rules == []:
            self.db.CreateBlueBallRuleTable()
        elif not self.rule_name in [x[1] for x in exist_rules]:
            self.db.AddBlueBallNewRule(self.rule_name, self.rule_type)

        self.UpdateRuleData();

    def CloseRule(self):
        self.db.close()
        
    @abstractmethod
    def GetRuleData(self):
        pass

class SsqBbrOccurTimes(SsqBbrController):
    def __init__(self):
        super().__init__('occur_times', 'INTEGER')

    def UpdateRuleData(self):
        print("更新蓝球出现次数...")
        
        for bbNo in range(1,17,1):
            try:
                get_sql = 'SELECT count(ssqid) FROM lottery_ssq WHERE ssqbb = {bbnum}'.format(bbnum = bbNo)
                get_occ_record = self.db.ExecuteSql(get_sql)
                update_sql = 'INSERT INTO blueball_rule(bb_id, {rule}) VALUES({bb_id}, {value})'.format(bb_id = bbNo, \
                                                                                                        rule = self.rule_name,
                                                                                                        value = get_occ_record[0][0])
                self.db.ExecuteSql(update_sql)
                print("蓝球{bno}共出现了{occ}次!".format(bno = bbNo, occ = get_occ_record[0][0]))
            except sqlite3.IntegrityError:
                get_sql = 'SELECT occur_times from blueball_rule where bb_id = {bb_id}'.format(bb_id = bbNo)
                old_value = self.db.ExecuteSql(get_sql)
                if old_value[0][0] == get_occ_record[0][0]:
                    continue
                
                print("已经存在数据，进行数据刷新...")
                update_sql = 'UPDATE blueball_rule SET occur_times = {value} WHERE bb_id = {bb_id}'.format(bb_id = bbNo, \
                                                                                                        value = get_occ_record[0][0])
                print("蓝球{bno}出现次数由{old_occ}刷新为{occ}!".format(bno = bbNo, old_occ = old_value[0][0], occ = get_occ_record[0][0]))
                self.db.ExecuteSql(update_sql)
            except:
                self.CloseRule()
                break;
                
        print("蓝球出现次数更新完成！")

    def GetRuleData(self):
        return self.db.ExecuteSql('select * from blueball_rule')

class SsqBbrOccurInternal(SsqBbrController):
    def __init__(self):
        super().__init__('occur_internal', 'VARCHAR')

    def UpdateRuleData(self):
        print("更新蓝球出现间隔...")
        get_occ_record = self.db.ExecuteSql('SELECT ssqbb from lottery_ssq')
        internal_rlt = [0 for x in range(1, 17, 1)]
        internal_rlt_times = [{} for x in range(1, 17, 1)]
        for data in get_occ_record:
            for bno in range(1, 17, 1):
                if bno != data[0]:
                    if 0 != internal_rlt[bno-1]:
                        internal_rlt[bno-1] += 1
                else:
                    if 0 != internal_rlt[bno-1]:
                        internal_rlt_times[bno-1][internal_rlt[bno-1]] = internal_rlt_times[bno-1].get(internal_rlt[bno-1], 0) + 1
                        #print(str(internal_rlt_times[bno-1]))
                        try:
                            update_sql = "UPDATE blueball_rule SET occur_internal = '{value}' WHERE bb_id = {bb_id}".format(bb_id = bno, \
                                                                                                                    rule = self.rule_name,
                                                                                                                    value = str(internal_rlt_times[bno-1]))
                            #print(update_sql)
                            self.db.ExecuteSql(update_sql)
                        except sqlite3.IntegrityError:
                            print("更新间隔失败！", error)
                            self.CloseRule()
                            exit(-1)
                        except sqlite3.OperationalError as error:
                            print("更新间隔失败！", error)
                            self.CloseRule()
                            exit(-1)
                    internal_rlt[bno-1] = 1

        #print(internal_rlt_times)
        print("蓝球出现间隔更新完成")

    def GetRuleData(self):
        return self.db.ExecuteSql('select bb_id,{row_name} from blueball_rule'.format(row_name = self.rule_name))

def RuleDataUpdate(rule):
    rule.UpdateRule()
    rule.CloseRule()

if __name__ == '__main__':
    """bbr = SsqBbrOccurTimes()
    bbr.UpdateRule()
    #bbd = bbr.GetRuleData()
    #for data in bbd:
    #    print(data)
    bbr.CloseRule()

    bbr = SsqBbrOccurInternal()
    bbr.UpdateRule()
    #for data in bbr.GetRuleData():
        #print(data)
    bbr.CloseRule()"""

    bbr_occt = SsqBbrOccurTimes()
    bbr_occint = SsqBbrOccurInternal()
    RuleDataUpdate(bbr_occt)
    RuleDataUpdate(bbr_occint)
