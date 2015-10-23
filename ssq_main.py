import SsqDbController as ssq_dbc
import SsqBlueballRuleController as ssq_bbrc
import SsqPredictTheNext as ssq_pdnt

dbcr = ssq_dbc.SsqDbController()
dbcr.OpenSsqDb()
dbcr.UpdateDb()
dbcr.CloseSsqDb()

ssq_bbrc.RuleDataUpdate(ssq_bbrc.SsqBbrOccurTimes())
ssq_bbrc.RuleDataUpdate(ssq_bbrc.SsqBbrOccurInternal())
ssq_bbrc.RuleDataUpdate(ssq_bbrc.SsqBbrFollowThere())

ssq_pdnt.WhichBlueBallIsTheBestInHistory()
ssq_pdnt.SpeBlueBallFit(12)
