"""Confere contratos e consistência das fixtures, sem testar o aplicativo C."""
from pathlib import Path
from collections import defaultdict
import csv, json, hashlib, math
from statistics import mean, stdev
from scipy.stats import t

BASE = Path(__file__).resolve().parent
OUT = BASE / 'dados'
TAG = 'SIMULADO_NAO_EXPERIMENTAL'

def rows(name):
    with (OUT / name).open(encoding='utf-8') as stream:
        data = list(csv.DictReader(stream))
    assert data and all(r['origin'] == TAG for r in data), name
    return data

def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-8, abs_tol=1e-7), (a, b)

def main():
    model = json.loads((OUT/'MODELO_SIMULADO.json').read_text())
    assert model['origin'] == TAG
    assert not model['core_runtime_validated'] and not model['real_requirements_closed']
    assert not model['fitted_to_real_data']
    manifests = rows('manifesto_simulado.csv')
    assert {r['file'] for r in manifests} == {p.name for p in OUT.iterdir() if p.name != 'manifesto_simulado.csv'}
    for r in manifests:
        p = OUT / r['file']
        assert p.parent == OUT and p.is_file()
        assert hashlib.sha256(p.read_bytes()).hexdigest() == r['sha256']
        assert p.stat().st_size == int(r['bytes'])
    plan = list(csv.DictReader((BASE.parents[2]/'configs/experiment_plan.csv').open()))
    expected = {p['scenario_id']: p for p in plan}
    requests, rounds = rows('requests_simuladas.csv'), rows('rounds_simuladas.csv')
    assert len(requests) == sum(int(p['concurrency'])*int(p['repetitions']) for p in plan)
    assert len(rounds) == sum(int(p['repetitions']) for p in plan)
    ids = {(r['run_id'],r['worker']) for r in requests}
    assert len(ids) == len(requests)
    grouped, by_cell = defaultdict(list), defaultdict(list)
    for r in requests:
        assert r['run_id'].startswith('SIM-') and r['clock_domain'] == 'SIMULATED_COORDINATOR'
        assert r['success'] == 'True' and r['error'] == '' and r['status_code'] == '200'
        start, end = float(r['start_s']), float(r['end_s'])
        assert 0 <= start < end
        close(r['elapsed_ms'],(end-start)*1000)
        if r['operation'] == 'HEAD':
            assert int(r['bytes']) == 0 and r['individual_mbps'] == ''
        else:
            assert int(r['bytes']) == int(r['file_size_bytes'])
            close(r['individual_mbps'],int(r['bytes'])*8/(end-start)/1e6)
        if r['operation'] == 'PUT': assert r['put_mode'] == 'overwrite'
        grouped[r['run_id']].append(r)
    assert len({r['run_id'] for r in rounds}) == len(rounds) == len(grouped)
    for r in rounds:
        p = expected[r['scenario_id']]
        g = grouped[r['run_id']]
        C = int(p['concurrency'])
        assert len(g) == C and {int(x['worker']) for x in g} == set(range(1,C+1))
        for field in ['profile','operation','file_size_bytes','concurrency']:
            assert r[field] == p[field] and all(x[field] == p[field] for x in g)
        release = float(r['release_s'])
        assert release <= min(float(x['start_s']) for x in g)
        close(r['end_s'],max(float(x['end_s']) for x in g))
        close(r['window_s'],float(r['end_s'])-release)
        assert int(r['successes']) == C and int(r['failures']) == 0
        assert int(r['bytes_ok']) == sum(int(x['bytes']) for x in g)
        close(r['response_ms'],mean(float(x['elapsed_ms']) for x in g))
        close(r['operations_per_s'],C/float(r['window_s']))
        if r['operation'] == 'HEAD':
            assert r['aggregate_mbps'] == r['individual_mbps'] == ''
        else:
            close(r['individual_mbps'],mean(float(x['individual_mbps']) for x in g))
            close(r['aggregate_mbps'],int(r['bytes_ok'])*8/float(r['window_s'])/1e6)
            assert 0 < float(r['aggregate_mbps']) <= float(p['bandwidth_mbps'])
        by_cell[r['scenario_id']].append(r)
    assert set(by_cell) == set(expected)
    for scenario, group in by_cell.items():
        assert {int(r['repetition']) for r in group} == set(range(1,int(expected[scenario]['repetitions'])+1))
    summaries = rows('resumo_simulado.csv')
    assert len(summaries) == len(plan)*3
    assert len({(r['scenario_id'],r['metric']) for r in summaries}) == len(summaries)
    for r in summaries:
        vals = [float(x[r['metric']]) for x in by_cell[r['scenario_id']] if x[r['metric']] != '']
        assert int(r['n']) == len(vals)
        if vals:
            avg, half = mean(vals), t.ppf(.975,len(vals)-1)*stdev(vals)/math.sqrt(len(vals))
            close(r['mean'],avg); close(r['ci95_low'],avg-half); close(r['ci95_high'],avg+half)
        else:
            assert r['mean'] == r['ci95_low'] == r['ci95_high'] == ''
    hashes = rows('integridade_simulada.csv')
    expected_hashes = {(r['run_id'],r['worker']):r for r in requests if r['operation'] != 'HEAD'}
    assert len(hashes) == len(expected_hashes) and {(r['run_id'],r['worker']) for r in hashes} == set(expected_hashes)
    for r in hashes:
        source = expected_hashes[(r['run_id'],r['worker'])]
        assert r['verification_basis'] == 'virtual_payload_only'
        assert r['hash_equal'] == 'True' and r['source_sha256'] == r['destination_sha256']
        assert len(r['source_sha256']) == 64 and float(r['verification_s']) > float(source['end_s'])
    for name, count in [('ping_simulado.csv',30),('iperf_simulado.csv',11),('traceroute_simulado.csv',5)]:
        cal = rows(name)
        assert len(cal) == 4*count
        assert {(r['profile'],r['direction']) for r in cal} == {(p,d) for p in ['A','B'] for d in ['cliente_servidor','servidor_cliente']}
        for p in ['A','B']:
            for d in ['cliente_servidor','servidor_cliente']:
                assert len([r for r in cal if r['profile']==p and r['direction']==d]) == count
    resources = rows('recursos_simulados.csv')
    assert len(resources) == len(rounds) and {r['run_id'] for r in resources} == set(grouped)
    negative = json.loads((OUT/'casos_negativos_simulados.json').read_text())
    assert negative['origin'] == TAG and negative['executed_against_application'] is False
    assert len(negative['cases']) == 6
    for r in negative['cases']:
        if 'success' in r:
            assert not r['success'] and r['throughput_mbps'] is None and r['error']
        if r['case'] == 'hash_mismatch': assert r['source_sha256'] != r['destination_sha256']
        if r['case'] == 'truncated_body': assert r['bytes'] < r['expected_bytes']
        if r['case'] == 'missing_worker': assert r['workers_observed'] < r['workers_expected']
        if r['case'] == 'duplicate_worker': assert len(set(r['ids'])) < len(r['ids'])
    print(f'Fixtures consistentes: {len(requests)} requisições, {len(rounds)} rodadas, {len(plan)} células, {len(hashes)} hashes virtuais, 6 casos negativos. Aplicativo C/CORE não executado.')

if __name__ == '__main__': main()
