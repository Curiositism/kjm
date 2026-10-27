import CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15
Ts=lambda P:CP.PropsSI('T','P',P*1e5,'Q',1,f)-K
H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P*1e5,f)/1e3
hg=lambda P:CP.PropsSI('H','P',P*1e5,'Q',1,f)/1e3
hf=lambda P:CP.PropsSI('H','P',P*1e5,'Q',0,f)/1e3
def comp(h1,P1,P2,eta):
    s=CP.PropsSI('S','P',P1*1e5,'H',h1*1e3,f); return h1+(CP.PropsSI('H','P',P2*1e5,'S',s,f)/1e3-h1)/eta
def Th(h,P): return CP.PropsSI('T','P',P*1e5,'H',h*1e3,f)-K
def dsh(h,P):  # T - Tsat, or quality if wet
    q=CP.PropsSI('Q','P',P*1e5,'H',h*1e3,f)
    return (Th(h,P)-Ts(P)) if not (0<=q<=1) else f"wet x={q:.3f}"
# base: snapshot 7
Pl,T11,Ph,P510,T14,eta1=2.693,100.02,21.493,20.863,146.20,0.672
def case(Pm=7.833,dT14=0,dSH1=0,inj_sh=0,x_inj=1.0,eta2=0.8,label=''):
    h1=H(T11+dSH1,Pl); h2=comp(h1,Pl,Pm,eta1)
    h6=H(T14+dT14,P510); x7=(h6-hf(Pm))/(hg(Pm)-hf(Pm))
    # injected stream = all flash vapor (quality x_inj means carryover liquid: inj mass = x7/x_inj fraction)
    hv=hg(Pm) if inj_sh==0 else H(Ts(Pm)+inj_sh,Pm)
    if x_inj<1: hv=hf(Pm)+x_inj*(hg(Pm)-hf(Pm)); finj=x7/x_inj
    else: finj=x7
    h3=(1-finj)*h2+finj*hv
    sh3=Th(h3,Pm)-Ts(Pm)
    h4=comp(h3,Pm,Ph,eta2) if sh3>0 else None
    out=dsh(h4,Ph) if h4 else 'n/a'
    print(f"{label:38s} Pm={Pm:6.3f} x7={x7:.3f} inj={finj:.3f} T2={Th(h2,Pm):6.2f} T3={Th(h3,Pm):6.2f} SH3={sh3:6.2f}  disch(eta2={eta2}) {out if isinstance(out,str) else f'{out:+.2f} K'}")
    return sh3
print("Tsat(P608)=",round(Ts(7.833),2))
case(label='base S7 (model)')
case(eta2=0.7,label='base S7 eta2 0.7')
case(dT14=-5,label='GC out T14 -5 K')
case(dT14=-10,label='GC out T14 -10 K')
case(dSH1=+5,label='1st-stage inlet SH +5 K')
case(dSH1=+10,label='1st-stage inlet SH +10 K')
case(inj_sh=10,label='injection vapor superheated +10 K')
case(inj_sh=20,label='injection vapor superheated +20 K')
for pm in (9.0,10.181): case(Pm=pm,label=f'intermediate P {pm} bar abs')
for xi in (0.98,0.95): case(x_inj=xi,label=f'liquid carryover, injection x={xi}')
# what injection quality explains measured T26? use S2, S3 (economizer balance closed) with measured states
print('--- injection quality consistent with measured T26 (S2,S3,S6), adiabatic mix, m703 measured ---')
for nm,(T06,P506,T26,P608,m1,mt) in {'S2':(121.89,5.24,106.83,5.37,1.63,2.29),'S3':(121.97,5.28,106.25,5.36,1.60,2.30),'S6':(130.33,6.43,110.16,6.41,1.61,2.75)}.items():
    Pa=lambda g:g+1.01325
    h2=H(T06,Pa(P506)); h3=H(T26,Pa(P608)); minj=mt-m1
    hinj=(mt*h3-m1*h2)/minj; q=(hinj-hf(Pa(P608)))/(hg(Pa(P608))-hf(Pa(P608)))
    loss=mt*(( m1*h2+minj*hg(Pa(P608)))/mt - h3)
    print(nm,f"h_inj needed={hinj:.1f}, x_inj={q:.3f} | or heat loss at mixing={loss:.1f} kW (if inj is sat vapor)")
