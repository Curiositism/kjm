import sys; sys.path.insert(0,'.')
import numpy as np, CoolProp.CoolProp as CP
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from states import states
f='R1336MZZZ'
D={'1':(313.250,3.374),'2':(432.909,3.274),'3':(433.920,3.274),'4':(479.199,3.164),"4'":(507.354,11.035),'4"':(483.992,10.985),
   '5':(504.309,38.49),'6':(504.309,38.42),'7':(423.689,37.72),'8':(423.689,11.035),'8f':(356.934,11.035),'9':(313.250,10.935)}
Pc=CP.PropsSI('Pcrit',f)/1e5; Pl=np.logspace(np.log10(1.5),np.log10(0.995*Pc),400)
fig,ax=plt.subplots(figsize=(7.4,5.2),dpi=200)
for q in (0,1): ax.plot([CP.PropsSI('H','P',p*1e5,'Q',q,f)/1e3 for p in Pl],Pl,color='#9a9a9a',lw=1.1)
def ln(S,seq,**k): ax.plot([S[s][0] for s in seq],[S[s][1] for s in seq],**k)
ln(D,['4',"4'",'4"','5','6','7','8','8f','9','1','2','3','4'],color='#b5651d',lw=1.3,marker='o',ms=3,label='design target')
for fn,c,lab in (('run/data.json','#dbe6f4','experiment snapshot 1 (11:39)'),('run/data2.json','#b6cbe8','experiment snapshot 2 (11:50)'),('run/data3.json','#86abdb','experiment snapshot 3 (11:57)'),('run/data4.json','#4a7fc1','experiment snapshot 4 (12:07)'),('run/data5.json','#163a6e','experiment snapshot 5 (12:13)'),('run/data6.json','#0e2a55','experiment snapshot 6 (12:16)'),('run/data7.json','#000814','experiment snapshot 7 (12:23)')):
    S,_=states(fn)
    ln(S,['1','2','3','4','5','6','7','8','9A','10A','11/12','13','1'],color=c,lw=1.5,marker='o',ms=3,label=lab)
ax.set_yscale('log'); ax.set_ylim(2,45); ax.set_xlim(290,520)
t=[2,3,4,6,8,10,15,20,30,40]; ax.set_yticks(t); ax.set_yticklabels([str(x) for x in t]); ax.minorticks_off()
ax.set_xlabel(r'$h$ (kJ kg$^{-1}$)'); ax.set_ylabel(r'$P$ (bar abs)'); ax.grid(alpha=.25,lw=.5)
ax.legend(fontsize=7.5,loc='upper left',frameon=False)
ax.text(.99,.01,'experiment: scenario A (T23 at P608), P abs = P_g + 1.01325 bar assumed',transform=ax.transAxes,ha='right',fontsize=6,color='#555')
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('run/ph_cmp3.png')
