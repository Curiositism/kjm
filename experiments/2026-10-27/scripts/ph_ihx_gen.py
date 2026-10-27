import CoolProp.CoolProp as CP, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f='R1336MZZZ'; PA=lambda g:(g+1.01325)  # bar abs
hs=lambda P,q:CP.PropsSI('H','P',P*1e5,'Q',q,f)/1e3
import sys; sys.path.insert(0,'.')
from states import states
S,X=states(sys.argv[1]); import json as _j; _d=_j.load(open(sys.argv[1]))
FL={'11/12','9B'}|({'4'} if _d['T12']<=CP.PropsSI('T','P',(_d['P508']+1.01325)*1e5,'Q',1,'R1336MZZZ')-273.15 else set())|({'5'} if _d['T13']<=CP.PropsSI('T','P',(_d['P509']+1.01325)*1e5,'Q',1,'R1336MZZZ')-273.15 else set()); OUT=sys.argv[2]; TAG=sys.argv[3]
Pc=CP.PropsSI('Pcrit',f)/1e5; Pl=np.logspace(np.log10(1.5),np.log10(0.98*Pc),300)
fig,ax=plt.subplots(figsize=(7.6,5.4),dpi=200)
for q in (0,1): ax.plot([hs(p,q) for p in Pl],Pl,color='#9a9a9a',lw=1.1)
B='#1f5fa8'; R='#c0392b'; G='#7f7f7f'
def ln(seq,**k):
    seq=[s for s in seq if s in S]; ax.plot([S[s][0] for s in seq],[S[s][1] for s in seq],**k)
ln(['1','2'],color=B,lw=1.7); ln(['3','4','5','6','7'],color=B,lw=1.7)
ln(['2','3'],color=B,lw=1.2); ln(['7','7v','3'],color=G,lw=1,ls='-.')
ln(['7','8'],color=B,lw=1.7)
ln(['8','9A','10A','11/12'],color=B,lw=1.7)
ln(['8','9B','10B'],color=B,lw=1,ls=':')
ln(['11/12','13','1'],color=B,lw=1.7)
# IHX highlight
for a,b in (('8','9A'),('11/12','13')): ln([a,b],color=R,lw=3,alpha=.45)
lab={'1':'1 C1 in','2':'2 C1 out','3':'3 C2 in','4':'4 C2 out' + (' = GC in' if '5' not in S else ''),'5':'5 GC in','6':'6 GC out','7':f"7 EXV1 out (x={X['x7']:.3f})",
     '7v':'7v','8':'8 IHX hot in','9A':'9A IHX hot out (T23@P608)','10A':f"10A evap in (x={X['x10A']:.3f})",
     '9B':'9B hf(P605) [alt]','10B':f"10B (x={X['x10B']:.3f}) [alt]",'11/12':'11 evap out = 12 IHX cold in*','13':'13 IHX cold out'}
off={'1':(-38,-12),'13':(8,-4),'2':(5,-10),'3':(-10,8),'4':(6,4),'5':(6,-10),'6':(-50,6),'7':(6,6),'7v':(-14,6),'8':(4,8),
     '9A':(-20,-16),'10A':(6,8),'9B':(6,-4),'10B':(-16,-14),'11/12':(-60,10)}
for k,(h,p) in S.items():
    alt=k in('9B','10B'); fl=k in FL
    ax.plot(h,p,'o',ms=5,mfc='white' if fl else B,mec=B,zorder=5,alpha=.6 if alt else 1)
    ax.annotate(lab[k],(h,p),textcoords='offset points',xytext=off[k],fontsize=6.8,color='#333')
ax.set_yscale('log'); ax.set_ylim(2.05,max(v[1] for v in S.values())*1.12); ax.set_xlim(285,500)
t=[x for x in (2.5,3,4,5,6,8,10,12,15,20,25,30) if x<=ax.get_ylim()[1]]; ax.set_yticks(t); ax.set_yticklabels([str(x) for x in t]); ax.minorticks_off()
ax.set_xlabel(r'$h$ (kJ kg$^{-1}$)'); ax.set_ylabel(r'$P$ (bar abs)'); ax.grid(alpha=.25,lw=.5)
ax.plot([],[],color=R,lw=3,alpha=.45,label='IHX hot side 8→9A / cold side 12→13')
ax.plot([],[],color=B,lw=1,ls=':',label='alternative path using P605 (flagged)')
ax.plot([],[],color=G,lw=1,ls='-.',label='economizer vapor injection 7→7v→3')
ax.plot([],[],'o',mfc='white',mec=B,label='T inconsistent with phase → placed on saturation line')
ax.legend(fontsize=7,loc='center',bbox_to_anchor=(0.55,0.42),frameon=False)
ax.text(.99,.01,'R1336mzz(Z), CoolProp 8.0.0; P abs = P_g + 1.01325 bar (assumed); *T24 not used (T<Tsat) | '+TAG,transform=ax.transAxes,ha='right',fontsize=6,color='#555')
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(OUT)
