import urllib.request
import re

#从乐彩网获取双色球历史数据
def GetSsqHistoryDataFromLecaiCom(startDate, endDate):
    """从乐彩网获取历史数据，起止日期格式：yyyy-mm-dd"""
    """现在不考虑：日期合法性，起止日期范围约束等"""
    url = r'http://www.lecai.com/lottery/draw/list/50/?type=range_date&start={START}&end={END}'.format(START = startDate, END = endDate)
    print(url)
    response = urllib.request.urlopen(url)
    the_page = response.read()
    return the_page.decode("utf-8")

#分析乐彩网数据
def ParseSsqHistoryDataFromLecaiCom(history_data_page):
    periodNumPat = re.compile(r'<td><a href="/lottery/draw/view/50\?phase=(\d{7})" target="_blank">(\d{7})</a></td>')
    datePat = re.compile(r'<td>(\d{4}-\d{2}-\d{2}).+</td>')
    redBallPat = re.compile(r'<em>(\d{2})</em><em>(\d{2})</em><em>(\d{2})</em><em>(\d{2})</em><em>(\d{2})</em><em>(\d{2})</em>')
    blueBallPat = re.compile(r'<em>(\d{2})</em>')

    matchState = {'periodNumPat':False, 'datePat':False, 'redBallPat':False, 'blueBallPat':False}
    matchRecord = {'periodNumPat':None, 'datePat':None, 'redBallPat':None, 'blueBallPat':None}

    lattery = []
    
    #这里有个大缓存，大小一万多，待优化
    historyList = history_data_page.splitlines()
    
    for line in historyList:
        line = line.strip()
        m = periodNumPat.match(line)
        if m != None:
            if m.group(1) != m.group(2):
                print('解析出来的期号不相等！group(1) = {0}, group(2) = {1}'.format(m.group(1), m.group(2)))
                break
            elif not matchState['periodNumPat']:                
                matchState['periodNumPat'] = True
                matchRecord['periodNumPat'] = m.group(1)
            else:
                print('解析到期号时有错误发生：连续匹配到期号')
                break

        m = datePat.match(line)
        if m != None:
            if matchState['periodNumPat'] and not matchState['datePat']:
                matchState['datePat'] = True
                matchRecord['datePat'] = m.group(1)
                #print(m.group(1))
            else:
                print('解析到日期时有错误发生：连续匹配到日期({datePat})或在没有匹配期号的情况下匹配到了日期({periodNumPat})'.format(**matchState))
                break

        m = redBallPat.match(line)
        if m != None:
            if matchState['periodNumPat'] and matchState['datePat'] and not matchState['redBallPat']:
                matchState['redBallPat'] = True
                matchRecord['redBallPat'] = m.groups()
                #print(m.groups())
            else:
                print('解析到红球时有错误发生：连续匹配到红球({redBallPat})或在没有匹配期号({periodNumPat})或没有匹配日期({datePat})的情况下匹配到了红球'.format(**matchState))
                break
        else:
            m = blueBallPat.match(line)
            if m != None:        
                if matchState['periodNumPat'] and matchState['datePat'] and matchState['redBallPat'] and not matchState['blueBallPat']:
                    matchState['blueBallPat'] = True              
                    matchRecord['blueBallPat'] = m.group(1)
                    #print(line)
                else:
                    print('解析到蓝球时有错误发生：连续匹配到红球({redBallPat})或在没有匹配期号({periodNumPat})或没有匹配日期({datePat})或没有匹配红球({redBallPat})的情况下匹配到了蓝球'.format(**matchState))
                    if any(matchState.values()):
                        print('终止抓取')
                        break
                    else:
                        print('本次错误忽略')
                        continue
                
        if matchState['blueBallPat']:
            if all(matchState.values()):
                yield matchRecord
                for key in matchState.keys():
                    matchState[key] = False
            else:
                print('有错误发生：蓝球已经解析({blueBallPat})时，期号({periodNumPat})、日期({datePat})、红球({redBallPat})或没匹配！'.format(**matchState))
                yield None
                break
    
#the_page = GetSsqHistoryDataFromLecaiCom('2014-01-09','2015-01-09')
#for num, ball in enumerate(ParseSsqHistoryDataFromLecaiCom(the_page),1):
#    print(ball)

#print('Total = %d'%num)
