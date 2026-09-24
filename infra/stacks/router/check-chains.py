# Offline check of config.yaml(.example): every fallback target exists, no paid chain
# reaches a free or uncensored model, and each job chain really walks in order.
# No API keys or network needed: every hop but the last is forced to fail.
#   python3 -m venv /tmp/ll && /tmp/ll/bin/pip install litellm pyyaml
#   /tmp/ll/bin/python check-chains.py config.yaml 2>/dev/null
import yaml, sys, copy, litellm
from litellm import Router
cfg=yaml.safe_load(open(sys.argv[1]))
ml=cfg['model_list']; ls=cfg['litellm_settings']
names=[m['model_name'] for m in ml]
dups={n for n in names if names.count(n)>1}; assert not dups, dups
fbs={k:v for d in ls['fallbacks'] for k,v in d.items()}
errors=[]
for k,v in fbs.items():
    for t in [k]+v:
        if t not in names: errors.append(f"{k}: unknown model {t}")
unc={'dolphin','cydonia','skyfall','unslopnemo','euryale','magnum','lunaris','mythomax','hf-stheno','hf-lunaris'}|{n for n in names if n.startswith('local-')}
model_of={m['model_name']:m['litellm_params']['model'] for m in ml}
for k,v in fbs.items():
    for t in [k]+v:
        if t in unc: errors.append(f"{k}: uncensored {t} in a chain")
        if 'free' not in k and (':free' in model_of[t] or model_of[t].endswith('openrouter/free')):
            errors.append(f"{k}: PAID chain reaches free model {t}")
print("static checks:", "OK" if not errors else errors)
# Simulate: every model fails except the LAST in each chain -> must end there, in order.
jobs=['general','general-free','code','code-free','reason','fast','vision','search','research','hermes','auto','auto-free','auto-code','auto-cheap','auto-search']
ok=True
for job in jobs:
    chain=[job]+fbs[job]; last=chain[-1]; tried=[]
    m2=[]
    for m in ml:
        m=copy.deepcopy(m); p=m['litellm_params']; p.pop('api_key',None); p['api_key']='x'
        if m['model_name']==last: p['mock_response']=f"answered-by:{last}"
        else: p['api_base']='http://127.0.0.1:9/v1'; p['model']='openai/x'
        m2.append(m)
    r=Router(model_list=m2,fallbacks=ls['fallbacks'],num_retries=0,max_fallbacks=10)
    try:
        out=r.completion(model=job,messages=[{"role":"user","content":"hi"}]).choices[0].message.content
    except Exception as ex: out=f"ERROR {type(ex).__name__}"
    good = out==f"answered-by:{last}"; ok&=good
    print(f"{'PASS' if good else 'FAIL'} {job:13} {' → '.join(chain)}  => {out}")
sys.exit(0 if ok and not errors else 1)
