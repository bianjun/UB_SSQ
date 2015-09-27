import sqlite3

class SsqSqlite3Db:
    def __init__(self, ssqdq ='cls_ssq.db'):
        self.dbfile = ssqdq
        self.dbconn = sqlite3.connect(ssqdq)
        self.dbcur = self.dbconn.cursor()
        #self.CreateSsqTable()

    def close(self):
        self.dbconn.commit()
        self.dbconn.close()

    def flush(self):
        self.dbconn.commit()

    #双色球基本表
    def CreateSsqTable(self):
        try:
            self.dbcur.execute("CREATE TABLE lottery_ssq ("
                  "ssqid VARCHAR(7) PRIMARY KEY, "
                  "ssqdt DATE, "
                  "ssqrb0 INTEGER, ssqrb1 INTEGER, ssqrb2 INTEGER, "
                  "ssqrb3 INTEGER, ssqrb4 INTEGER, ssqrb5 INTEGER, "
                  "ssqbb INTEGER)")
        except sqlite3.OperationalError as dbExpInfo:
            if str(dbExpInfo).find('table lottery_ssq already exists'):
                #print(dbExpInfo)
                pass
            else:
                print(dbExpInfo)

    def GetTableNames(self):
        self.dbcur.execute("PRAGMA table_info(lottery_ssq)")  
        return self.dbcur.fetchall()

    def InsertSingleHistoryRecordToSsqTable(self, historyRecord):
        try:
            hisBalls = historyRecord.replace(' ', ',')
            sql = "INSERT INTO lottery_ssq(ssqid, ssqdt, ssqrb0, ssqrb1, ssqrb2, ssqrb3, ssqrb4, ssqrb5, ssqbb) VALUES("\
                  + hisBalls + ")"
            #print(sql)
            self.dbcur.execute(sql)
        except sqlite3.IntegrityError as dbExpInfo:
            self.dbconn.rollback()
            print(dbExpInfo)
            
    def WriteLotteryFromFileToDb(self, lotteryFile):
        try:
            with open(lotteryFile) as lottery:
                for balls in lottery:
                    self.InsertSingleHistoryRecordToSsqTable(balls.rstrip())
        except IOException as ioexp:
            print(ioexp)
            return

    def GetRedBall(self, redBallId, redBallNo, num = -1):
        redBalls = ('ssqrb0', 'ssqrb1', 'ssqrb2', 'ssqrb3', 'ssqrb4', 'ssqrb5')
        sql = 'select rowid, ssqid, {0} from lottery_ssq where {0} = {1} limit {2}'.format(redBalls[redBallId], redBallNo, num)
        dbRecord = self.dbcur.execute(sql).fetchall()
        return dbRecord

    def GetBlueBall(self, blueBallNo, num = -1):
        sql = 'select rowid, ssqid, ssqbb from lottery_ssq where ssqbb = {0} limit {1}'.format(blueBallNo, num)
        dbRecord = self.dbcur.execute(sql).fetchall()
        return dbRecord

    def GetAllRecord(self, num = -1):
        sql = 'select rowid, * from lottery_ssq ORDER BY ssqid limit {limit}'.format(limit = num)
        dbRecord = self.dbcur.execute(sql).fetchall()
        return dbRecord

    def ShowLotteryDb(self):
        sql = 'select rowid, * from lottery_ssq'
        dbRecord = self.dbcur.execute(sql).fetchall()
        #print(dbRecord)

        for record in dbRecord:
            print(record)

    def FoundLatestSsq(self):
        sql = 'select max(ssqid) from lottery_ssq'
        dbRecord = self.dbcur.execute(sql).fetchall()
        return dbRecord

    #规则表基本操作
    def GetRulesName_c(self, table):
        """获取规则名称"""
        self.dbcur.execute("PRAGMA table_info({0})".format(table))  
        return self.dbcur.fetchall()

    def AddNewRule_c(self, table, ruleName, ruleType):
        sql = 'ALTER TABLE {0} ADD {1} {2}'.format(table,ruleName,ruleType)
        self.dbcur.execute(sql)

    def DeployNewRule_c(self, table, ruleName, DeployNewRuleFunc):
        ssqRecord = self.GetAllRecord()
        sql = ''
        for data in ssqRecord:
            ruleValue = DeployNewRuleFunc(data)
            sql = 'INSERT INTO {table}(ssqid, {ruleName}) values({data[1]}, {ruleValue})'.format(table, ruleName, data, ruleValue)
            #print(sql)
            self.dbcur.execute(sql)
            
    #双色球基本规则表
    def CreateSsqRuleTable(self):
        try:
            self.dbcur.execute("CREATE TABLE lottery_ssq_rule ("
                  "ssqid VARCHAR(7) PRIMARY KEY, "
                  "FOREIGN KEY(ssqid) REFERENCES lottery_ssq(ssqid))")
        except sqlite3.OperationalError as dbExpInfo:
            if str(dbExpInfo).find('already exists'):
                print(dbExpInfo)
            else:
                print(dbExpInfo)
                
    def GetRulesName(self):
        """获取规则名称"""
        self.dbcur.execute("PRAGMA table_info(lottery_ssq_rule)")  
        return self.dbcur.fetchall()

    def AddNewRule(self, ruleName, ruleType):
        sql = 'ALTER TABLE lottery_ssq_rule ADD {0} {1}'.format(ruleName, ruleType)
        self.dbcur.execute(sql)

    def DeployNewRule(self, ruleName, DeployNewRuleFunc):
        ssqRecord = self.GetAllRecord()
        sql = ''
        for data in ssqRecord:
            ruleValue = DeployNewRuleFunc(data)
            sql = 'INSERT INTO lottery_ssq_rule(ssqid,{0}) values({1}, {2})'.format(ruleName, data[1], ruleValue)
            #print(sql)
            self.dbcur.execute(sql)

    def GetAllRuleValues(self, ruleName, num = -1):
        sql = 'SELECT rowid, ssqid, {0} from lottery_ssq_rule limit {1}'.format(ruleName, num)
        return self.dbcur.execute(sql).fetchall()

    def GetSpeRuleValues(self, ruleName, logicRel, ruleValue, num = -1):
        """logicRel: =, <, >.etc"""
        sql = 'SELECT rowid, ssqid, {0} from lottery_ssq_rule WHERE {0} {1} {2} limit {3}'.format(ruleName, logicRel, ruleValue, num)
        #print(sql)
        return self.dbcur.execute(sql).fetchall()

    #蓝球规则表
    def CreateBlueBallRuleTable(self):
        sql = 'CREATE TABLE blueball_rule(bb_id INTEGER PRIMARY KEY)'
        self.dbcur.execute(sql)

    def GetBlueBallRulesName(self):
        return self.GetRulesName_c('blueball_rule')

    def AddBlueBallNewRule(self, ruleName, ruleType):
        self.AddNewRule_c('blueball_rule', ruleName, ruleType)

    def DeployBlueBallNewRule(self, bbNo, ruleName, DeployNewBbRuleFunc, num = -1):
        sql = 'SELECT rowid, * from lottery_ssq where ssqbb = {ssqbb} limit {limit}'.format(ssqbb = bbNo, limit = num)
        #print(sql)
        ruleValue = DeployNewBbRuleFunc(self.dbcur.execute(sql).fetchall())
        sql = 'INSERT INTO blueball_rule(bb_id, {rule}) VALUES({bb_id}, {value})'.format(bb_id = bbNo, rule = ruleName, value = ruleValue)
        self.dbcur.execute(sql)

    def GetBlueBallAllRule(self, bbNo, ruleName, num = -1):
        sql = 'SELECT bb_id, {rule} FROM blueball_rule WHERE bb_id = {bb_id} LIMIT {limit}'.format(rule = ruleName, bb_id = bbNo, limit = num)
        return self.dbcur.execute(sql).fetchall()

    def GetBlueBallRules(self, num = -1):
        sql = 'SELECT * FROM blueball_rule ORDER BY bb_id LIMIT {limit}'.format(limit=num)
        return self.dbcur.execute(sql).fetchall()

#testDb = SsqSqlite3Db()
#testDb.InsertSingleHistoryRecordToSsqTable('2012047 06 07 11 16 32 33 11')
#testDb.WriteLotteryFromFileToDb(r'F:/python_code/Allball.txt')
#testDb.ShowLotteryDb()
#testDb.flush()

#redball = testDb.GetRedBall(1, 2)
#print(len(redball), redball)

#blueball = testDb.GetBlueBall(16)
#print(len(blueball), blueball)

#allRecord = testDb.GetAllRecord(10)
#print(allRecord)
#print(len(allRecord), allRecord[0][2:])

#testDb.CreateSsqRuleTable()
#print(testDb.GetRulesName())
#testDb.AddNewRule('ssq_sum', 'INTEGER')
#print(testDb.GetRulesName())
#testDb.DeployNewRule('ssq_sum', lambda record: sum(record[2:]))
#print(testDb.GetAllRuleValues('ssq_sum', 10))
#print(testDb.GetSpeRuleValues('ssq_sum', '=', 117))

#testDb.CreateBlueBallRuleTable()
#print(testDb.GetBlueBallRulesName())
#testDb.AddBlueBallNewRule('ocur_times', 'INTEGER')
#testDb.DeployBlueBallNewRule(1, 'ocur_times', lambda record: len(record))
#testDb.DeployBlueBallNewRule(6, 'ocur_times', lambda record: len(record))
#print(testDb.GetBlueBallAllRule(6, 'ocur_times'))
#print(testDb.GetBlueBallRules())

#testDb.close()

if __name__ == '__main__':
    testDb = SsqSqlite3Db()
    testDb.CreateSsqTable()
    ball = {'redBallPat': ('01', '07', '20', '24', '25', '33'), 'periodNumPat': '2015015', 'datePat': '2015-02-03', 'blueBallPat': '04'}
    testDb.InsertSingleHistoryRecordToSsqTable("{ssqid} '{ssqdt}' {readballs} {blueball}".format(ssqid = ball['periodNumPat'], ssqdt = ball['datePat'], readballs = " ".join(ball['redBallPat']), blueball = ball['blueBallPat']))
    print(testDb.GetAllRecord(10))
    testDb.close()
