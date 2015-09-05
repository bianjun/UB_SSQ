import os
from datetime import date,timedelta
import time
import GetSsqHistoryData as gsd
import Cls_SsqSqlite3Db
#import CommFunc as cf

class SsqDbController:
    def __init__(self):
        self.ssqDb = None
        
    def OpenSsqDb(self):
        """如果基本信息表不存在则创建，有则打开"""
        self.ssqDb = Cls_SsqSqlite3Db.SsqSqlite3Db()
        ssqDbTableInfoList = [(0, 'ssqid', 'VARCHAR(7)', 0, None, 1), (1, 'ssqdt', 'VARCHAR(10)', 0, None, 0), (2, 'ssqrb0', 'INTEGER', 0, None, 0), (3, 'ssqrb1', 'INTEGER', 0, None, 0), (4, 'ssqrb2', 'INTEGER', 0, None, 0), (5, 'ssqrb3', 'INTEGER', 0, None, 0), (6, 'ssqrb4', 'INTEGER', 0, None, 0), (7, 'ssqrb5', 'INTEGER', 0, None, 0), (8, 'ssqbb', 'INTEGER', 0, None, 0)]
        if ssqDbTableInfoList != self.ssqDb.GetTableNames():
            self.ssqDb.CreateSsqTable()
            print('SsqTable is not created, create it now!')
            if ssqDbTableInfoList != self.ssqDb.GetTableNames():
                print('Error: The ssqDb.CreateSsqTable() cannot create correct table')
            else:
                print('SsqTable created successfully!')

    def UpdateDb(self):
        """获取当前最新的数据，并根据当前日期更新最新的数据到数据库"""
        latestSsq = self.ssqDb.FoundLatestSsq()
        begindate = date(2003, 1, 1)
        #print(latestSsq)
        today = date.today()
        if [(None,)] != latestSsq:
            print(latestSsq)
        else:
            print('双色球基本表还没有数据，从2003年1月1日开始更新数据库，更新到今天:', str(today))
            deltaDays = today - begindate
            if deltaDays.days < 0:
                print('今天比数据库最新时间还早，请确认系统时间是否正确？')
                #这里后面需要抛出异常
                return
            elif deltaDays == 0:
                print('数据库数据已经是最新！')
                return
            else:
                updateEndDate = begindate
                while deltaDays.days > 0:
                    updateDays = 365 if deltaDays.days >= 365 else deltaDays.days
                    updateEndDate = updateEndDate + timedelta(updateDays)
                    deltaDays = today - updateEndDate
                    print(updateEndDate)
                    #for ssqdata in gsd.GetSsqHistoryDataFromLecaiCom(begindate, updateEndDate):
                
    def CloseSsqDb(self):
        self.ssqDb.close()
        

#the_page = gsd.GetSsqHistoryDataFromLecaiCom('2003-1-1','2003-5-1')
#num = 0
#for num, ball in enumerate(gsd.ParseSsqHistoryDataFromLecaiCom(the_page),1):
#    print(ball)

#print('Total = %d'%num)

dbcr = SsqDbController()
dbcr.OpenSsqDb()
dbcr.UpdateDb()
dbcr.CloseSsqDb()
