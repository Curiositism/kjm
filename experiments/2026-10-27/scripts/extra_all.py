import sys,json,CoolProp.CoolProp as CP
f='R1336MZZZ';K=273.15
d=json.load(open(sys.argv[1])); A=1.01325
PA=lambda g,a=A:(g+a)*1e5
H=lambda T,P:CP.PropsSI('H','T',T+K,'P',P,f)/1e3
hf=lambda P:CP.PropsSI('H','P',P,'Q',0,f)/1e3; hg=lambda P:CP.PropsSI('H','P',P,'Q',1,f)/1e3
Ts=lambda P:CP.PropsSI('T','P',P,'Q',0,f)-K
def HV(T,P):
    return hg(P) if T<=CP.PropsSI('T','P',P,'Q',1,f)-K else H(T,P)
def HL(T,P):
    return hf(P) if T>=Ts(P)-0.01 else H(T,P)
Psg=lambda T:CP.PropsSI('P','T',T+K,'Q',0,f)/1e5-A
def bis(g,a,b):
    fa=g(a)
    for _ in range(80):
        c=(a+b)/2; fc=g(c)
        if fa*fc<=0: b=c
        else: a,fa=c,fc
    return (a+b)/2
m1,m3=d['m701'],d['m703']
print("x7 sensitivity:")
xs=[]
for a in (0.98,A,1.03):
    for dT in (-0.5,0,0.5):
        xs.append(CP.PropsSI('Q','P',PA(d['P603'],a),'H',H(d['T14']+dT,PA(d['P510'],a))*1e3,f))
h6=H(d['T14'],PA(d['P510'])); P7=PA(d['P603'])
print(f" h6={h6:.2f} hf={hf(P7):.2f} hg={hg(P7):.2f} x7={(h6-hf(P7))/(hg(P7)-hf(P7)):.4f} range {min(xs):.4f}-{max(xs):.4f}")
P8=PA(d['P608']); h8=HL(d['T22'],P8); h9A=HL(d['T23'],P8); h9B=hf(PA(d['P605']))
P10=PA(d['P601']); h11=hg(PA(d['P602'])); h13=H(d['T25'],PA(d['P507']))
for nm,h9 in (('A',h9A),('B',h9B)):
    x10=CP.PropsSI('Q','P',P10,'H',h9*1e3,f)
    print(f"scen {nm}: h9={h9:.2f} x10={x10:.4f} Qev={m3*(h11-h9):.1f} IHXhot={m3*(h8-h9):.1f}")
print(f"IHX cold={m3*(h13-h11):.1f}  h8={h8:.2f} h11={h11:.2f} h13={h13:.2f}")
qc=h13-h11
print(f"T23 needed for balance={bis(lambda T:h8-HL(T,P8)-qc,40,d['T22']-0.01):.2f}; cold-in T needed (A)={CP.PropsSI('T','P',PA(d['P602']),'H',(h13-(h8-h9A))*1e3,f)-K:.2f}")
for Tc,nm in ((d['T16'],'T16'),(d['T24'],'T24')): print(f"eps {nm}: {(d['T25']-Tc)/(d['T22']-Tc):.3f}")
print(f"rho liq EOS T23@P608={CP.PropsSI('D','T',d['T23']+K,'P',P8,f):.1f}; sat liq at Tsat(P605)={CP.PropsSI('D','P',PA(d['P605']),'Q',0,f):.1f}; 409={d['rho409']*1000:.1f}")
print(f"Psat(T23) bar.g={Psg(d['T23']):.3f} vs P605 {d['P605']}")
for nm,T,Pg in (("T15/P601",d['T15'],d['P601']),("T16/P602",d['T16'],d['P602']),("T22/P608",d['T22'],d['P608'])):
    print(f" {nm}: Psat(T)={Psg(T):.3f} read {Pg} diff {Pg-Psg(T):+.3f}")
# compressors
h1=HV(d['T11'],PA(d['P507'])); h2=HV(d['T06'],PA(d['P506'])); h3=HV(d['T26'],P8); h4=HV(d['T12'],PA(d['P508']))
flag4=d['T12']<=CP.PropsSI('T','P',PA(d['P508']),'Q',1,f)-K
def eta(ha,Pa,hb,Pb):
    s=CP.PropsSI('S','P',Pa,'H',ha*1e3,f); return (CP.PropsSI('H','P',Pb,'S',s,f)/1e3-ha)/(hb-ha)
mi=m1-m3; h3m=(m3*h2+mi*hg(P8))/m1
print('eta2: not computable (T12<=Tsat)' if flag4 else '',end=' ')
print(f"eta2 measured T26={eta(h3,P8,h4,PA(d['P508'])):.3f}; eta2 with mix h3={h3m:.1f} (T={CP.PropsSI('T','P',P8,'H',h3m*1e3,f)-K:.2f}) -> {eta(h3m,P8,h4,PA(d['P508'])):.3f}")
r1=CP.PropsSI('D','T',d['T11']+K,'P',PA(d['P507']),f); r2=CP.PropsSI('D','T',d['T06']+K,'P',PA(d['P506']),f)
r3=CP.PropsSI('D','T',d['T26']+K,'P',P8,f); r4=CP.PropsSI('D','P',PA(d['P508']),'Q',1,f) if flag4 else CP.PropsSI('D','T',d['T12']+K,'P',PA(d['P508']),f)
print(f"V1in={m3/r1:.4f} ratio1={r2/r1:.3f}; V2in={m1/r3:.4f} ratio2={r4/r3:.3f}")
print(f"econ energy in={m1*h6:.1f} out={m3*h8+mi*hg(P8):.1f}; x_inj energy={(h6-h8)/(hg(P8)-h8):.4f}; flow frac={(mi/m1):.4f}")
print(f"408 {d.get('rho408',0)*1000:.1f} vs sat vap @P608 {CP.PropsSI('D','P',P8,'Q',1,f):.1f}")
print(f"superheats: C1in {d['T11']-Ts(PA(d['P507'])):.2f} C1out {d['T06']-Ts(PA(d['P506'])):.2f} C2in {d['T26']-Ts(P8):.2f} C2out {d['T12']-Ts(PA(d['P508'])):.2f} GCin {d['T13']-Ts(PA(d['P509'])):.2f} GCsub {Ts(PA(d['P510']))-d['T14']:.2f}")
print(f"GC approach T14-T03={d['T14']-d['T03']:.2f}; GC dP={d['P509']-d['P510']:.2f}; evap Tsat in/out {Ts(P10):.2f}/{Ts(PA(d['P602'])):.2f}; T02-Tsat(602)={d['T02']-Ts(PA(d['P602'])):.2f}")
# water side
Tm=(d['T03']+d['T04'])/2; Pw=PA((d['P503']+d['P504'])/2) if 'P503' in d and 'P504' in d else PA(2.6)  # water-side pressure: measured mean if given
rw=CP.PropsSI('D','T',Tm+K,'P',Pw,'Water'); cw=CP.PropsSI('C','T',Tm+K,'P',Pw,'Water')/1e3
mw=rw*d['V610']/3600; print(f"GC water rho={rw:.1f} cp={cw:.4f} mw={mw:.3f} Q={mw*cw*(d['T04']-d['T03']):.1f}")
if 'P505' in d:
    hw=CP.PropsSI('H','T',d['T04']+K,'P',PA(d['P504']),'Water'); a=CP.PropsSI('H','P',PA(d['P505']),'Q',0,'Water'); b=CP.PropsSI('H','P',PA(d['P505']),'Q',1,'Water')
    x=(hw-a)/(b-a); print(f"flash Tsat={CP.PropsSI('T','P',PA(d['P505']),'Q',0,'Water')-K:.2f} vs T05 {d['T05']}; x={x:.5f}; steam={x*mw*3.6:.3f} t/h")
Tm=(d['T01']+d['T02'])/2; r=CP.PropsSI('D','T',Tm+K,'P',3e5,'Water'); c=CP.PropsSI('C','T',Tm+K,'P',3e5,'Water')/1e3
for nm,h9 in (('A',h9A),('B',h9B)): print(f"src water LPM ({nm}) = {m3*(h11-h9)/(c*(d['T01']-d['T02']))/r*60000:.0f}")
print(f"dash backcalc: m703*h11={m3*h11:.1f}, m703*hf(P603)={m3*hf(P7):.1f}")
