import CoolProp.CoolProp as CP, numpy as np, json, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f='R1336MZZZ';K=273.15
# design table read from the screenshot: state, T[C], P[kPa], h[kJ/kg]
D=[('1',71.07,337.4,313.250),('2',70.00,327.4,432.909),('3',71.00,327.4,433.920),
   ('4',115.21,316.4,479.199),("4'",152.58,1103.5,507.354),('4"',132.74,1098.5,483.992),
   ('5',194.84,3849.0,504.309),('6',194.75,3842.0,504.309),('7',164.00,3772.0,423.689),('8',120.14,1103.5,423.689),
   ('8g',120.14,1103.5,468.359),('8f',120.14,1103.5,356.934),('9',89.49,1093.5,313.250)]
print("design check (P read as absolute kPa): state, h_design, h_CoolProp(T,P) or note, Tsat(P)")
for s,T,P,h in D:
    Pa=P*1e3; ts=CP.PropsSI('T','P',Pa,'Q',0,f)-K if Pa<CP.PropsSI('Pcrit',f) else float('nan')
    try: hc=CP.PropsSI('H','T',T+K,'P',Pa,f)/1e3
    except Exception as e: hc=float('nan')
    print(f"{s:3s} h_d={h:8.3f} h_CP={hc:8.3f} Tsat={ts:7.2f} T-Tsat={T-ts:+6.2f}")
print("x8 from h:",round(CP.PropsSI('Q','P',1103.5e3,'H',423.689e3,f),4)," x1:",round(CP.PropsSI('Q','P',337.4e3,'H',313.25e3,f),4))
print("design Pm sqrt:",round((3849*316.4)**0.5,1))
# experiment states (abs, atm 1.01325 bar) from cycle_report output
E={'1':(453.5,2.663),'2':(476.2,6.433),'3':(463.3,6.553),'4':(482.4,12.853),'5':(482.3,12.393),'6':(354.9,12.103),
   '7':(354.9,6.543),'8':(321.7,6.553),'9':(297.9,4.093),'10':(297.9,3.163),'11':(432.3,3.203),'13':(455.8,2.663)}
Pc=CP.PropsSI('Pcrit',f); Pl=np.logspace(np.log10(1.5e5),np.log10(0.995*Pc),400)
fig,ax=plt.subplots(figsize=(7.2,5.2),dpi=200)
for q in (0,1): ax.plot([CP.PropsSI('H','P',p,'Q',q,f)/1e3 for p in Pl],Pl/1e5,color='#8a8a8a',lw=1.1)
dd={s:(h,P/100) for s,T,P,h in D}
def path(S,seq,**k): ax.plot([S[s][0] for s in seq],[S[s][1] for s in seq],**k)
path(dd,['4',"4'",'4"','5','6','7','8'],color='#b5651d',lw=1.4,label='design target (screenshot table)')
path(dd,['8f','9','1','2','3','4'],color='#b5651d',lw=1.4,ls='--')
path(E,['1','2','3','4','5','6','7'],color='#1f5fa8',lw=1.6,label='experiment snapshot (2026-10-27 11:12 screen)')
path(E,['7','8','9','10','11','13','1'],color='#1f5fa8',lw=1.6,ls='--')
for S,c in ((dd,'#b5651d'),(E,'#1f5fa8')):
    for s,(h,p) in S.items(): ax.plot(h,p,'o',ms=4,color=c); ax.annotate(s,(h,p),textcoords='offset points',xytext=(4,3),fontsize=7,color=c)
ax.set_yscale('log'); ax.set_ylim(2,45); ax.set_xlim(270,540)
t=[2,3,4,6,8,10,15,20,30,40]; ax.set_yticks(t); ax.set_yticklabels([str(x) for x in t]); ax.minorticks_off()
ax.set_xlabel(r'$h$ (kJ kg$^{-1}$)'); ax.set_ylabel(r'$P$ (bar abs)'); ax.grid(alpha=.25,lw=.5)
ax.legend(fontsize=7.5,loc='upper left',frameon=False)
ax.text(0.99,0.01,'Exp. point 9 placed at $h_f(P_{605})$ (flagged); P abs = P_g + 1.01325 bar assumed',transform=ax.transAxes,ha='right',fontsize=6.5,color='#555')
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('run/ph_vs_design.png')
