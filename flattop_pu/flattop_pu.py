import openmc

# PU-MET-FAST-006 (Flattop-Pu): Pu 구를 천연 우라늄 반사체가 감쌈
# 원자밀도 [atoms/b-cm]

# Pu-Ga 합금 코어 (δ상)
core = openmc.Material(name='Core')
core.set_density('sum')
core.add_nuclide('Pu239', 3.6697e-02)
core.add_nuclide('Pu240', 1.8700e-03)
core.add_nuclide('Pu241', 1.1639e-04)
core.add_element('Ga', 1.4755e-03)

# 천연 우라늄 반사체
reflector = openmc.Material(name='Reflector')
reflector.set_density('sum')
reflector.add_nuclide('U234', 2.6438e-06)
reflector.add_nuclide('U235', 3.4610e-04)
reflector.add_nuclide('U238', 4.7721e-02)

mats = openmc.Materials([core, reflector])
mats.export_to_xml()

# 코어 구 r = 4.5332 cm, 반사체 외반경 24.1420 cm, 바깥은 진공
inner = openmc.Sphere(r=4.5332)
outer = openmc.Sphere(r=24.1420, boundary_type='vacuum')
cell_core = openmc.Cell(fill=core, region=-inner)
cell_refl = openmc.Cell(fill=reflector, region=+inner & -outer)
geom = openmc.Geometry([cell_core, cell_refl])
geom.export_to_xml()

settings = openmc.Settings()
settings.batches = 200
settings.inactive = 10
settings.particles = 10000
settings.export_to_xml()

openmc.run()

n = settings.batches
with openmc.StatePoint(f'statepoint.{n}.h5') as sp:
    keff = sp.keff
    print(f'Final k-effective = {keff}')
