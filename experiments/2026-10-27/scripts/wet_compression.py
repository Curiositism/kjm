#!/usr/bin/env python3
"""2nd-stage wet-compression margin: minimum inlet superheat for dry discharge (assumed eta2, optional heat loss)."""
import CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15
Ts=lambda P:CP.PropsSI('T','P',P*1e5,'Q',1,f)-K
def h2(Pin,Pout,sh,eta,ql):
    T=Ts(Pin)+sh+K
    h1=CP.PropsSI('H','T',T,'P',Pin*1e5,f); s=CP.PropsSI('S','T',T,'P',Pin*1e5,f)
    return h1+(CP.PropsSI('H','P',Pout*1e5,'S',s,f)-h1)/eta-ql*1e3
def min_sh(Pin,Pout,eta,ql=0.0,target=0.0):
    hg=CP.PropsSI('H','P',Pout*1e5,'Q',1,f); lo,hi=0.01,80.0
    for _ in range(60):
        m=(lo+hi)/2; h=h2(Pin,Pout,m,eta,ql)
        ok=(h>hg) and (CP.PropsSI('T','P',Pout*1e5,'H',h,f)-K-Ts(Pout)>=target)
        hi,lo=(m,lo) if ok else (hi,m)
    return (lo+hi)/2
if __name__=='__main__':
    cases={'S4':(7.803,16.893,8.84),'S7':(7.833,21.493,7.65),'S8':(8.033,23.173,8.75),'S9':(8.563,25.363,8.58),'S10':(8.783,27.273,8.80)}
    for k,(pi,po,sh) in cases.items():
        print(k,'measured',sh,'| min eta0.8/0.7:',round(min_sh(pi,po,0.8),2),round(min_sh(pi,po,0.7),2),
              '| +5K eta0.8:',round(min_sh(pi,po,0.8,0,5),2),'| eta0.8 loss 3/6 kJ/kg:',round(min_sh(pi,po,0.8,3),2),round(min_sh(pi,po,0.8,6),2))
