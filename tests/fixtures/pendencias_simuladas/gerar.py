"""Gera somente fixtures sintéticas; não executa CORE, sockets ou clientes C."""
from pathlib import Path
import csv, json, random, hashlib, math
import numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = BASE / 'dados'
SEED = 20261105
TAG = 'SIMULADO_NAO_EXPERIMENTAL'

def write_csv(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def digest_payload(size, corrupt=False):
    # Conteúdo virtual determinístico, sem copiar arquivos reais da campanha.
    block = bytes(range(256)) * 4096
    h = hashlib.sha256()
    if corrupt:
        block = b'X' + block[1:]
    for _ in range(size // len(block)):
        h.update(block)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    plan = list(csv.DictReader((ROOT/'configs/experiment_plan.csv').open()))
    profiles = {}
    for p in plan:
        profiles[p['profile']] = (float(p['bandwidth_mbps']), float(p['delay_oneway_ms']))
    ping, iperf, hops = [], [], []
    for profile, (bandwidth, delay) in profiles.items():
        for direction in ['cliente_servidor', 'servidor_cliente']:
            for sample in range(1,31):
                ping.append(dict(origin=TAG,profile=profile,direction=direction,sample=sample,
                    rtt_ms=2*delay+1+rng.uniform(-.3,.3),lost=False))
            for rep in range(1,12):
                rate = bandwidth * rng.uniform(.94,.96)
                iperf.append(dict(origin=TAG,profile=profile,direction=direction,repetition=rep,
                    window_s=30,omitted_start_s=3,mbps=rate,bytes=rate*1e6*30/8))
            route = ['10.10.1.1','10.10.2.2','10.10.3.2','10.10.4.2','10.10.5.10'] if direction=='cliente_servidor' else [
                '10.10.5.1','10.10.4.1','10.10.3.1','10.10.2.1','10.10.1.10']
            for hop, address in enumerate(route,1):
                hops.append(dict(origin=TAG,profile=profile,direction=direction,hop=hop,address=address,
                    rtt_ms=.2*hop+(2*delay if hop>=3 else 0)+rng.uniform(0,.15)))
    req, rounds, hashes, resources = [], [], [], []
    virtual_clock = 0.0
    hash_map = {size:digest_payload(size) for size in [2*2**20,10*2**20]}
    for p in plan:
        C, size, repetitions = int(p['concurrency']), int(p['file_size_bytes']), int(p['repetitions'])
        op, profile = p['operation'], p['profile']
        B, delay = profiles[profile]
        for rep in range(1,repetitions+1):
            run_id = f"SIM-{p['scenario_id']}-r{rep:02d}"
            release = virtual_clock
            # Modelo ideal de compartilhamento. Não ajustado aos resultados reais.
            utilization = {1:.75,8:.94,32:.95}[C] * rng.uniform(.98,1.0)
            rate = B*.94*utilization
            rtt_s = (2*delay+1)/1000
            persistence_s = .012 if op=='PUT' else .003
            duration = 2*rtt_s + (0 if op=='HEAD' else C*size*8/(rate*1e6)) + persistence_s
            group=[]
            for worker in range(1,C+1):
                start = release + rng.uniform(0,.002)
                end = release + duration * rng.uniform(.99,1)
                elapsed = end-start
                count = 0 if op=='HEAD' else size
                row=dict(origin=TAG,scenario_id=p['scenario_id'],profile=profile,operation=op,
                         file_size_bytes=size,concurrency=C,run_id=run_id,repetition=rep,worker=worker,
                         clock_domain='SIMULATED_COORDINATOR',start_s=start,end_s=end,
                         elapsed_ms=elapsed*1000,bytes=count,status_code=200,success=True,
                         individual_mbps=None if op=='HEAD' else count*8/elapsed/1e6,
                         error='',put_mode='overwrite' if op=='PUT' else 'not_applicable')
                group.append(row); req.append(row)
                if op!='HEAD':
                    hashes.append(dict(origin=TAG,run_id=run_id,worker=worker,operation=op,
                        file_size_bytes=size,source_sha256=hash_map[size],destination_sha256=hash_map[size],
                        verification_s=end+.01,verification_basis='virtual_payload_only',hash_equal=True))
            end = max(r['end_s'] for r in group)
            window = end-release
            agg = None if op=='HEAD' else C*size*8/window/1e6
            rounds.append(dict(origin=TAG,scenario_id=p['scenario_id'],profile=profile,operation=op,
                bandwidth_mbps=B,delay_oneway_ms=delay,file_size_bytes=size,concurrency=C,run_id=run_id,
                repetition=rep,clock_domain='SIMULATED_COORDINATOR',release_s=release,end_s=end,window_s=window,
                launch_skew_ms=(max(r['start_s'] for r in group)-min(r['start_s'] for r in group))*1000,
                successes=C,failures=0,bytes_ok=0 if op=='HEAD' else C*size,
                response_ms=sum(r['elapsed_ms'] for r in group)/C,
                individual_mbps=None if op=='HEAD' else sum(r['individual_mbps'] for r in group)/C,
                aggregate_mbps=agg,operations_per_s=C/window))
            resources.append(dict(origin=TAG,run_id=run_id,scope='whole_simulated_host',
                cpu_pct=8+min(30,C*.6)+rng.uniform(0,3),rss_mib=200+5*C+rng.uniform(0,10),
                io_mib_s=0 if op=='HEAD' else C*size/window/2**20,
                cache_policy='uniform_warm_assumed',persistence='PUT_fsync_assumed'))
            virtual_clock=end+.1
    for name,data in [('ping_simulado.csv',ping),('iperf_simulado.csv',iperf),('traceroute_simulado.csv',hops),
                      ('requests_simuladas.csv',req),('rounds_simuladas.csv',rounds),
                      ('integridade_simulada.csv',hashes),('recursos_simulados.csv',resources)]:
        write_csv(name,data)
    summaries=[]
    for p in plan:
        group=[r for r in rounds if r['scenario_id']==p['scenario_id']]
        for metric in ['response_ms','individual_mbps','aggregate_mbps']:
            x=np.array([r[metric] for r in group if r[metric] is not None])
            n=len(x); avg=float(x.mean()) if n else None
            std=float(x.std(ddof=1)) if n>1 else None
            half=float(t.ppf(.975,n-1)*std/math.sqrt(n)) if n>1 else None
            summaries.append(dict(origin=TAG,scenario_id=p['scenario_id'],profile=p['profile'],operation=p['operation'],
                size_mib=int(p['file_size_bytes'])/2**20,concurrency=int(p['concurrency']),metric=metric,n=n,
                mean=avg,median=float(np.median(x)) if n else None,std=std,
                ci95_low=avg-half if half is not None else None,ci95_high=avg+half if half is not None else None))
    write_csv('resumo_simulado.csv',summaries)
    negatives=[
        dict(case='timeout',status_code=0,bytes=0,error='timeout',success=False,throughput_mbps=None),
        dict(case='not_found',status_code=404,bytes=0,error='remote_file_not_found',success=False,throughput_mbps=None),
        dict(case='truncated_body',status_code=200,bytes=1000,expected_bytes=2097152,error='truncated',success=False,throughput_mbps=None),
        dict(case='hash_mismatch',status_code=200,bytes=2097152,error='integrity',success=False,throughput_mbps=None,
             source_sha256=hash_map[2*2**20],destination_sha256=digest_payload(2*2**20,True)),
        dict(case='missing_worker',workers_expected=8,workers_observed=7,expected_action='exclude_incomplete_round'),
        dict(case='duplicate_worker',ids=['SIM-run-w01','SIM-run-w01'],expected_action='reject_duplicate')]
    (OUT/'casos_negativos_simulados.json').write_text(json.dumps({'origin':TAG,'executed_against_application':False,
        'cases':negatives},ensure_ascii=False,indent=2)+'\n')
    metadata=dict(origin=TAG,seed=SEED,core_runtime_validated=False,real_requirements_closed=False,
        fitted_to_real_data=False,clock='virtual seconds, no UTC measurement',profiles=profiles,
        model='B*.94*{1:.75,8:.94,32:.95}[C]*U(.98,1); duration=2RTT+C*bits/rate+persistence',
        head='no payload; no content throughput',hashes='computed on virtual repeated bytes(range(256))',
        trace='plausible IP route model, not observed packet route',
        put='all successful PUTs modeled as overwrite; real collector uses per-attempt names',
        resources='illustrative whole-host values; no performance causal inference',
        dependencies={m:__import__(m).__version__ for m in ['numpy','scipy','matplotlib']})
    (OUT/'MODELO_SIMULADO.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    for metric,label in [('aggregate_mbps','Goodput agregado (Mbit/s)'),('response_ms','Tempo médio (ms)')]:
        fig,axes=plt.subplots(2,2,figsize=(11,7))
        for i,op in enumerate(['GET','PUT']):
            for j,profile in enumerate(['A','B']):
                ax=axes[i,j]
                for size in [2,10]:
                    g=[r for r in summaries if r['operation']==op and r['profile']==profile and r['size_mib']==size and r['metric']==metric]
                    ax.errorbar([r['concurrency'] for r in g],[r['mean'] for r in g],
                                yerr=[(r['ci95_high']-r['ci95_low'])/2 for r in g],marker='o',capsize=4,label=f'{size} MiB')
                ax.set(title=f'{op}, perfil {profile}',xlabel='Concorrência',ylabel=label,xticks=[1,8,32]);ax.legend();ax.grid(alpha=.2)
        fig.suptitle('SIMULAÇÃO — NÃO SÃO RESULTADOS DO CORE\nIC95% entre rodadas sintéticas; platô definido pelo modelo')
        fig.tight_layout();fig.savefig(OUT/f'{metric}_SIMULADO.png',dpi=150);plt.close(fig)
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!='manifesto_simulado.csv':
            manifest.append(dict(origin=TAG,file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    write_csv('manifesto_simulado.csv',manifest)
    print(f'SIMULADO: {len(req)} requisições, {len(rounds)} rodadas, {len(plan)} células. Saída: {OUT}')
if __name__=='__main__': main()
