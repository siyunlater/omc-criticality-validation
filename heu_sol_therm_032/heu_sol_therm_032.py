import argparse

import openmc
import openmc.stats

# HEU-SOL-THERM-032: 농축 우라늄 질산염 용액 구 (반사체 없음), 알루미늄 용기
# 원자밀도 [atoms/b-cm]
parser = argparse.ArgumentParser()
parser.add_argument("--batches", type=int, default=1000)
parser.add_argument("--inactive", type=int, default=50)
parser.add_argument("--particles", type=int, default=10000)
args = parser.parse_args()

# 우라닐 질산염 용액 (물 속 수소는 열산란 데이터 S(α,β) 필요)
sol = openmc.Material(name='Uranium Nitrate Solution')
sol.set_density('sum')
sol.add_nuclide('U233', 3.9124e-09)
sol.add_nuclide('U234', 4.0905e-07)
sol.add_nuclide('U235', 3.6157e-05)
sol.add_nuclide('U236', 2.0858e-07)
sol.add_nuclide('U238', 1.9878e-06)
sol.add_nuclide('N14', 1.1212e-04)
sol.add_nuclide('H1', 6.6409e-02)
sol.add_nuclide('O16', 3.3588265e-02)
sol.add_nuclide('O17', 1.2734779e-05)
sol.add_s_alpha_beta('c_H_in_H2O')

# Type 1100 알루미늄 용기
al = openmc.Material(name='Type 1100 Aluminum')
al.set_density('sum')
al.add_nuclide('Al27', 5.9881e-02)
al.add_nuclide('Si28', 2.0096847e-04)
al.add_nuclide('Si29', 1.0204606e-05)
al.add_nuclide('Si30', 6.7269216e-06)
al.add_nuclide('Fe54', 6.404951e-06)
al.add_nuclide('Fe56', 1.005440332e-04)
al.add_nuclide('Fe57', 2.3220002e-06)
al.add_nuclide('Fe58', 3.090156e-07)
al.add_nuclide('Cu63', 3.5518206e-05)
al.add_nuclide('Cu65', 1.5845794e-05)
al.add_nuclide('Mn55', 1.4853e-05)

mats = openmc.Materials([sol, al])
mats.export_to_xml()

# 용액 구 r = 61.011 cm, 용기 외반경 61.786 cm, 바깥은 진공
inner = openmc.Sphere(r=61.011)
outer = openmc.Sphere(r=61.786, boundary_type='vacuum')
cell_sol = openmc.Cell(fill=sol, region=-inner)
cell_al = openmc.Cell(fill=al, region=+inner & -outer)
geom = openmc.Geometry([cell_sol, cell_al])
geom.export_to_xml()

settings = openmc.Settings()
settings.batches = args.batches
settings.inactive = args.inactive
settings.particles = args.particles
# 큰 구(r = 61 cm)라 소스가 퍼지는 데 시간이 걸림 → 중심 작은 상자에서 시작
settings.source = openmc.IndependentSource(
    space=openmc.stats.Box((-1, -1, -1), (1, 1, 1)))
# 소스 수렴 확인용 Shannon 엔트로피 (inactive 배치 수를 정당화하는 근거)
mesh = openmc.RegularMesh()
mesh.lower_left = (-62, -62, -62)
mesh.upper_right = (62, 62, 62)
mesh.dimension = (10, 10, 10)
settings.entropy_mesh = mesh
settings.export_to_xml()

openmc.run()

n = settings.batches
with openmc.StatePoint(f'statepoint.{n}.h5') as sp:
    keff = sp.keff
    print(f'Final k-effective = {keff}')
    # 엔트로피가 inactive 이후 평평해지는지 확인
    h = sp.entropy
    k = args.inactive
    print(f'entropy: batch 1 = {h[0]:.3f}, 마지막 inactive = {h[k-1]:.3f}, '
          f'active 평균 = {h[k:].mean():.3f} ± {h[k:].std():.3f}')
