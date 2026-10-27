#!/usr/bin/env python3
"""R1336mzz(Z) 2-stage VI heat pump snapshot -> P-h diagram + consistency report.
python3 -I cycle_report.py data.json out.png   (T: degC, P: bar.g, flows kg/s, rho g/mL, V610 m3/h)"""
import sys, json, numpy as np, CoolProp.CoolProp as CP
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f='R1336MZZZ'; K=273.15; A=101325.0
d=json.load(open(sys.argv[1])); out=sys.argv[2]
Pa=lambda g:g*1e5+A
hg=lambda P:CP.PropsSI('H','P',P,'Q',1,f)/1e3
hf=lambda P:CP.PropsSI('H','P',P,'Q',0,f)/1e3
Ts=lambda P:CP.PropsSI('T','P',P,'Q',1,f)-K
H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P,f)/1e3
def st(T,P,role):
    ts=Ts(P)
    if role=='v': return (H(T,P),False,T-ts) if T>=ts else (hg(P),True,T-ts)
    return (H(T,P),False,T-ts) if T<=ts else (hf(P),True,T-ts)
P24=d.get('P24',d['P602'])
pts=[('1','압축기1 입구','T11','P507','v'),('2','압축기1 출구','T06','P506','v'),
     ('3','압축기2 입구','T26','P608','v'),('4','압축기2 출구','T12','P508','v'),
     ('5','GC 입구','T13','P509','v'),('6','GC 출구','T14','P510','l'),
     ('8','Econ 액','T22','P608','l'),('9','IHX 고압출구','T23','P605','l'),
     ('11','증발기 출구','T16','P602','v'),('12','IHX 저압입구','T24',None,'v'),('13','IHX 저압출구','T25','P507','v')]
S={}; print(f"{'점':>3s} {'위치':12s}{'T':>8s}{'P(abs)':>8s}{'Tsat':>8s}{'T-Tsat':>8s}{'h':>8s}")
for k,lab,tc,pc,role in pts:
    P=Pa(P24) if pc is None else Pa(d[pc]); h,fl,dT=st(d[tc],P,role); S[k]=(h,P,fl)
    print(f"{k:>3s} {lab:12s}{d[tc]:8.2f}{P/1e5:8.3f}{Ts(P):8.2f}{dT:+8.2f}{h:8.1f}{'  *T<Tsat(vap)/T>Tsat(liq)' if fl else ''}")
P7=Pa(d['P603']); x7=CP.PropsSI('Q','P',P7,'H',S['6'][0]*1e3,f); S['7']=(S['6'][0],P7,False)
S['7v']=(hg(Pa(d['P608'])),Pa(d['P608']),False)
P10=Pa(d['P601']); x10=CP.PropsSI('Q','P',P10,'H',S['9'][0]*1e3,f); T10=CP.PropsSI('T','P',P10,'H',S['9'][0]*1e3,f)-K
S['10']=(S['9'][0],P10,False)
print(f"\nEXV1→Econ 입구: x7={x7:.4f}, T={Ts(P7):.2f}°C | Econ 액 T22={d['T22']} vs Tsat(P608)={Ts(Pa(d['P608'])):.2f}")
print(f"EXV2→증발기 입구: x10={x10:.4f}, T={T10:.2f}°C (측정 T15={d['T15']})")
m1=d.get('m701'); m3=d.get('m703')
if m1 and m3: print(f"질량수지: 분사량 m701-m703={m1-m3:+.2f} kg/s, 예상(x7·m701)={x7*m1:.2f} kg/s, 예상 액량 (1-x7)m701={(1-x7)*m1:.2f} vs m703={m3}")
res={}
for nm,a,b,mm in (('1단','1','2',m3),('2단','3','4',m1)):
    ha,Pa_,fa=S[a]; hb,Pb,fb=S[b]
    s=CP.PropsSI('S','P',Pa_,'H',ha*1e3,f); hs=CP.PropsSI('H','P',Pb,'S',s,f)/1e3
    Ts_=CP.PropsSI('T','P',Pb,'S',s,f)-K; eta=(hs-ha)/(hb-ha) if not(fa or fb) else float('nan')
    W=(hb-ha)*mm if mm else float('nan'); res[nm]=W
    print(f"{nm}: PR={Pb/Pa_:.3f}, η_is={eta:.3f}, Δh={hb-ha:.1f} kJ/kg, W={W:.0f} kW, 이상토출 T={Ts_:.1f}°C")
if m1:
    h3=(1-x7)*S['2'][0]+x7*S['7v'][0]; T3=CP.PropsSI('T','P',S['3'][1],'H',h3*1e3,f)-K
    print(f"혼합 예측 T26(x7 기준)={T3:.1f}°C vs 측정 {d['T26']}")
if d.get('rho407'):
    for nm,pc in (('P508','P508'),('P509','P509')):
        print(f"밀도 407 측정 {d['rho407']*1000:.1f} vs EOS(T12,{nm})={CP.PropsSI('D','T',d['T12']+K,'P',Pa(d[pc]),f):.1f} kg/m3")
if d.get('rho409'): print(f"밀도 409 측정 {d['rho409']*1000:.0f} vs EOS(T23,P605)={CP.PropsSI('D','T',d['T23']+K,'P',Pa(d['P605']),f):.0f} kg/m3")
Qgc=m1*(S['5'][0]-S['6'][0]) if m1 else float('nan'); Qev=m3*(S['11'][0]-S['10'][0]) if m3 else float('nan')
print(f"\nGC 냉매측 Q={Qgc:.0f} kW | 증발기 냉매측 Q={Qev:.0f} kW | 압축일 합 {sum(res.values()):.0f} kW | Qgc-(Qev+W)={Qgc-Qev-sum(res.values()):+.0f} kW")
if d.get('V610'):
    Tm=(d['T03']+d['T04'])/2; r=CP.PropsSI('D','T',Tm+K,'P',3e5,'Water'); c=CP.PropsSI('C','T',Tm+K,'P',3e5,'Water')/1e3
    print(f"GC 수측 Q={r*d['V610']/3600*c*(d['T04']-d['T03']):.0f} kW (ΔT={d['T04']-d['T03']:.2f} K)")
if m3 and d.get('T01'):
    Tm=(d['T01']+d['T02'])/2; r=CP.PropsSI('D','T',Tm+K,'P',3e5,'Water'); c=CP.PropsSI('C','T',Tm+K,'P',3e5,'Water')/1e3
    print(f"증발기 냉매측 Q 기준 열원수 필요유량={Qev/(c*(d['T01']-d['T02']))/r*60000:.0f} LPM (704 유량계 무효 시 참고)")
qh=(S['8'][0]-S['9'][0]); qc=(S['13'][0]-S['12'][0])
if m3: print(f"IHX 고압측 {m3*qh:.0f} kW vs 저압측 {m3*qc:.0f} kW")
Pc=CP.PropsSI('Pcrit',f); Pl=np.logspace(np.log10(0.7e5),np.log10(0.9*Pc),300)
fig,ax=plt.subplots(figsize=(7.2,5.2),dpi=200)
for fn in (hf,hg): ax.plot([fn(p) for p in Pl],Pl/1e5,color='#8a8a8a',lw=1.2)
seq=['1','2','3','4','5','6','7']; ax.plot([S[k][0] for k in seq],[S[k][1]/1e5 for k in seq],color='#1f5fa8',lw=1.6)
seq=['7','8','9','10','11','12','13','1']; ax.plot([S[k][0] for k in seq],[S[k][1]/1e5 for k in seq],color='#1f5fa8',lw=1.6,ls='--')
ax.plot([S['7'][0],S['7v'][0],S['3'][0]],[S['7'][1]/1e5,S['7v'][1]/1e5,S['3'][1]/1e5],color='#555',lw=1,ls='-.')
for a,b in (('1','2'),('3','4')):
    s=CP.PropsSI('S','P',S[a][1],'H',S[a][0]*1e3,f); pp=np.linspace(S[a][1],S[b][1],30)
    ax.plot([CP.PropsSI('H','P',p,'S',s,f)/1e3 for p in pp],pp/1e5,color='#c0392b',lw=1,ls=':')
for k,(h,p,fl) in S.items():
    ax.plot(h,p/1e5,'o',ms=6,mfc='white' if fl else '#1f5fa8',mec='#1f5fa8',zorder=5)
    ax.annotate(k,(h,p/1e5),textcoords='offset points',xytext=(5,4),fontsize=9)
ps=[v[1]/1e5 for v in S.values()]; hs_=[v[0] for v in S.values()]
ax.set_yscale('log'); ax.set_ylim(min(ps)*0.8,max(ps)*1.25); ax.set_xlim(min(hs_)-25,max(hs_)+25)
ticks=[t for t in (1,1.5,2,3,4,5,6,8,10,12,15) if ax.get_ylim()[0]<=t<=ax.get_ylim()[1]]
ax.set_yticks(ticks); ax.set_yticklabels([str(t) for t in ticks]); ax.minorticks_off()
ax.set_xlabel(r'$h$ (kJ kg$^{-1}$)'); ax.set_ylabel(r'$P$ (bar abs)'); ax.grid(alpha=.25,lw=.5)
ax.plot([],[],'o',mfc='white',mec='#1f5fa8',label=r'$T$ inconsistent with phase: placed on saturation line')
ax.plot([],[],color='#c0392b',ls=':',label='isentropic reference'); ax.plot([],[],color='#555',ls='-.',label='economizer vapor injection (7→7v→3)')
ax.legend(fontsize=7.5,loc='upper left',frameon=False)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(out)
