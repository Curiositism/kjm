import json,CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15
def states(fn):
    d=json.load(open(fn)); PA=lambda g:g+1.01325
    H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P*1e5,f)/1e3
    hs=lambda P,q:CP.PropsSI('H','P',P*1e5,'Q',q,f)/1e3
    def HV(T,P):  # vapor-side point: T at or below Tsat -> placed on saturated vapor (as in cycle_report.py)
        ts=CP.PropsSI('T','P',P*1e5,'Q',1,f)-K
        return hs(P,1) if T<=ts else H(T,P)
    S={'1':(HV(d['T11'],PA(d['P507'])),PA(d['P507'])),'2':(HV(d['T06'],PA(d['P506'])),PA(d['P506'])),
       '3':(HV(d['T26'],PA(d['P608'])),PA(d['P608'])),'4':(HV(d['T12'],PA(d['P508'])),PA(d['P508'])),
       '5':(HV(d['T13'],PA(d['P509'])),PA(d['P509'])),'6':(H(d['T14'],PA(d['P510'])),PA(d['P510']))}
    # rule: if 2nd-stage discharge is superheated (T12 > Tsat(P508)), the high-pressure side is anchored on point 4 (GC inlet point 5 dropped)
    sh4=d['T12']-(CP.PropsSI('T','P',PA(d['P508'])*1e5,'Q',1,f)-K)
    if sh4>0: S.pop('5')
    S['7']=(S['6'][0],PA(d['P603'])); S['7v']=(hs(PA(d['P608']),1),PA(d['P608']))
    def HL(T,P):
        ts=CP.PropsSI('T','P',P*1e5,'Q',0,f)-K
        return hs(P,0) if T>=ts-0.01 else H(T,P)
    S['8']=(HL(d['T22'],PA(d['P608'])),PA(d['P608'])); S['9A']=(H(d['T23'],PA(d['P608'])),PA(d['P608']))
    S['10A']=(S['9A'][0],PA(d['P601'])); S['9B']=(hs(PA(d['P605']),0),PA(d['P605'])); S['10B']=(S['9B'][0],PA(d['P601']))
    S['11/12']=(hs(PA(d['P602']),1),PA(d['P602'])); S['13']=(HV(d['T25'],PA(d['P507'])),PA(d['P507']))
    x=lambda h,P:CP.PropsSI('Q','P',P*1e5,'H',h*1e3,f)
    return S,{'x7':x(*S['7']),'x10A':x(*S['10A']),'x10B':x(*S['10B'])}
