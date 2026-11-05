"""Extrai medições de comandos/ sem executar rede ou misturar dados sintéticos."""
from pathlib import Path
from collections import defaultdict
from statistics import mean
import csv
import hashlib
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/reports/comparacao_core'
SIM = ROOT / 'tests/fixtures/pendencias_simuladas/dados'

def csv_read(path):
    with path.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))

def csv_write(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, measured, comparison, routes = [], [], [], []
    sim_ping = csv_read(SIM/'ping_simulado.csv')
    sim_iperf = csv_read(SIM/'iperf_simulado.csv')
    sim_trace = csv_read(SIM/'traceroute_simulado.csv')
    for profile, folder in [('A','comandosip/comandosip'),('B','comandosipB/comandosipB')]:
        base = ROOT/'comandos'/folder
        texts = {}
        for p in sorted(base.glob('*.txt')):
            texts[p.name] = p.read_text(encoding='utf-8-sig')
            manifest.append(dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        assert len(texts) == 6, base
        for direction, pingfile, ratefile, tracefile in [
            ('cliente_servidor','ping_client.txt','iperf_client.txt','traceroute_client.txt'),
            ('servidor_cliente','ping_server.txt','iperfR_server.txt','traceroute_server.txt')]:
            ping = texts[pingfile]
            stats = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms',ping)
            count = re.search(r'(\d+) packets transmitted, (\d+) received, ([\d.]+)% packet loss',ping)
            assert stats and count
            low,avg,high,dev = map(float, stats.groups())
            sent,received,loss = map(float, count.groups())
            text = texts[ratefile]
            receiver = re.search(r'0\.00-([\d.]+)\s+sec\s+[\d.]+\s+MBytes\s+([\d.]+)\s+Mbits/sec\s+receiver', text)
            sender = re.search(r'0\.00-([\d.]+)\s+sec\s+[\d.]+\s+MBytes\s+([\d.]+)\s+Mbits/sec\s+(\d+)\s+sender', text)
            assert receiver and sender
            reverse = 'Reverse mode, remote host 10.10.5.10 is sending' in text
            assert reverse == (direction == 'servidor_cliente')
            row = dict(origin='MEDICAO_FORNECIDA_CORE',profile=profile,direction=direction,
                nominal_mbps=100 if profile=='A' else 20,ping_sent=int(sent),ping_received=int(received),ping_loss_pct=loss,
                rtt_min_ms=low,rtt_avg_ms=avg,rtt_max_ms=high,rtt_mdev_ms=dev,
                iperf_receiver_mbps=float(receiver[2]),iperf_receiver_window_s=float(receiver[1]),
                iperf_sender_mbps=float(sender[2]),iperf_sender_window_s=float(sender[1]),retransmissions=int(sender[3]),
                independent_iperf_runs=1,ping_source=str((base/pingfile).relative_to(ROOT)),iperf_source=str((base/ratefile).relative_to(ROOT)))
            measured.append(row)
            sp = [float(r['rtt_ms']) for r in sim_ping if r['profile']==profile and r['direction']==direction]
            si = [float(r['mbps']) for r in sim_iperf if r['profile']==profile and r['direction']==direction]
            comparison.append(dict(profile=profile,direction=direction,real_rtt_avg_ms=avg,
                simulated_rtt_avg_ms=mean(sp),real_minus_simulated_rtt_ms=avg-mean(sp),real_ping_samples=int(sent),simulated_ping_samples=len(sp),
                real_receiver_mbps=row['iperf_receiver_mbps'],simulated_iperf_avg_mbps=mean(si),
                real_minus_simulated_mbps=row['iperf_receiver_mbps']-mean(si),real_iperf_runs=1,simulated_iperf_runs=len(si)))
            hops = re.findall(r'^\s*(\d+)\s+([\d.]+)\s+\([\d.]+\)\s+([\d.]+) ms\s+([\d.]+) ms\s+([\d.]+) ms',texts[tracefile],re.M)
            assert len(hops)==5
            model_route = [r['address'] for r in sim_trace if r['profile']==profile and r['direction']==direction]
            assert [h[1] for h in hops] == model_route
            for hop,ip,a,b,c in hops:
                routes.append(dict(origin='MEDICAO_FORNECIDA_CORE',profile=profile,direction=direction,hop=int(hop),address=ip,
                    probe1_rtt_ms=float(a),probe2_rtt_ms=float(b),probe3_rtt_ms=float(c),source=str((base/tracefile).relative_to(ROOT))))
    csv_write('calibracao_extraida.csv',measured)
    csv_write('comparacao_real_simulado.csv',comparison)
    csv_write('rotas_extraidas.csv',routes)
    csv_write('fontes_sha256.csv',manifest)
    records = [json.loads(p.read_text()) for p in sorted((ROOT/'experiments/raw/json').glob('S*.json'))]
    byround = defaultdict(list)
    for r in records:
        result=r['client_result']
        assert result['status']=='ok' and r['client_exit_code']==0
        byround[(r['scenario_id'],r['repetition'])].append(r)
    cells=defaultdict(list)
    for (scenario,rep), group in byround.items():
        first=group[0]
        assert len(group)==first['concurrency']
        vals=[r['client_result'] for r in group]
        cells[scenario].append(dict(profile=first['profile'],operation=vals[0]['method'],file_size_bytes=first['file_size_bytes'],
            concurrency=first['concurrency'],elapsed_ms=mean(v['elapsed_ms'] for v in vals),
            individual_mbps=None if vals[0]['method']=='HEAD' else mean(v['throughput_mbps'] for v in vals)))
    app=[]
    for scenario,rows in sorted(cells.items()):
        row=rows[0]
        app.append(dict(scenario_id=scenario,profile=row['profile'],operation=row['operation'],file_size_bytes=row['file_size_bytes'],
            concurrency=row['concurrency'],n_rounds=len(rows),mean_elapsed_ms=mean(r['elapsed_ms'] for r in rows),
            mean_individual_mbps=None if row['operation']=='HEAD' else mean(r['individual_mbps'] for r in rows)))
    csv_write('aplicacao_conferida.csv',app)
    synthetic = csv_read(SIM/'resumo_simulado.csv')
    app_comparison=[]
    for row in app:
        for metric,field in [('response_ms','mean_elapsed_ms'),('individual_mbps','mean_individual_mbps')]:
            sim=next(s for s in synthetic if s['scenario_id']==row['scenario_id'] and s['metric']==metric)
            measured_value=row[field]
            modeled_value=float(sim['mean']) if sim['mean'] else None
            app_comparison.append(dict(scenario_id=row['scenario_id'],profile=row['profile'],operation=row['operation'],
                file_size_bytes=row['file_size_bytes'],concurrency=row['concurrency'],metric=metric,
                real_mean=measured_value,simulated_mean=modeled_value,
                real_minus_simulated=None if measured_value is None else measured_value-modeled_value))
    csv_write('comparacao_aplicacao_simulada.csv',app_comparison)
    print('Comparação com o modelo ideal:',[r for r in app_comparison if r['scenario_id'] in ['S004','S006','S022','S024']])
    fig,axes=plt.subplots(1,2,figsize=(12.8,7.2))
    colors=['#1773a6','#e29229']
    for j,direction in enumerate(['cliente_servidor','servidor_cliente']):
        group=[r for r in measured if r['direction']==direction]
        xs=[i+(j-.5)*.32 for i in range(2)]
        label='Cliente → servidor' if j==0 else 'Servidor → cliente'
        for ax,key,ylabel in [(axes[0],'iperf_receiver_mbps','Taxa recebida (Mbit/s)'),(axes[1],'rtt_avg_ms','RTT médio (ms)')]:
            bars=ax.bar(xs,[r[key] for r in group],width=.30,label=label,color=colors[j])
            ax.bar_label(bars,labels=[f'{r[key]:.1f}'.replace('.',',') for r in group],padding=4,fontsize=12)
            ax.set_xticks([0,1],['Perfil A','Perfil B']);ax.set_ylabel(ylabel,fontsize=13)
            ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    axes[0].set_ylim(0,115);axes[1].set_ylim(0,50)
    axes[0].set_title('iperf: resultado no receptor',fontsize=15)
    axes[1].set_title('ping: ida e volta',fontsize=15)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.1),ncol=2,frameon=False,fontsize=12)
    fig.suptitle('Rede medida no CORE',fontsize=22,y=.94)
    fig.text(.5,.045,'Por perfil e sentido: 1 ensaio iperf de cerca de 20 s; 10 pings.\nSem IC entre ensaios independentes de calibração.',ha='center',fontsize=11)
    fig.subplots_adjust(left=.08,right=.97,top=.82,bottom=.24,wspace=.25)
    for ext in ['png','svg']: fig.savefig(OUT/f'calibracao_core.{ext}',dpi=200)
    plt.close(fig)
    print(json.dumps({'calibracao':measured,'comparacao':comparison,'aplicacao_destaques':[r for r in app if
        (r['operation']=='GET' and r['file_size_bytes']==10485760 and r['concurrency'] in [1,32]) or
        (r['operation']=='PUT' and r['file_size_bytes']==10485760 and r['concurrency']==1) or
        (r['operation']=='HEAD' and r['file_size_bytes']==2097152 and r['concurrency']==1)]},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
