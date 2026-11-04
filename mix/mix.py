import openmc

# delta-phase plutonium
pu = openmc.Material()
pu.set_density('sum')
pu.add_nuclide('Pu239', 3.7291e-02)
pu.add_nuclide('Pu240', 1.9277e-03)
pu.add_nuclide('Pu241', 1.2196e-04)
pu.add_nuclide('Ga69', 8.1915e-04)
pu.add_nuclide('Ga71', 5.4365e-04)

# HEU
u = openmc.Material()
u.set_density('sum')
u.add_nuclide('U235', 4.4892e-02)
u.add_nuclide('U238', 3.2340e-03)
mats = openmc.Materials([pu, u])

mats.export_to_xml()

# Plutonium sphere surrounded by HEU
sphere1 = openmc.Sphere(r=5.0419)
sphere2 = openmc.Sphere(r=6.7056, boundary_type='vacuum')
cell1 = openmc.Cell(fill=pu, region=-sphere1)
cell2 = openmc.Cell(fill=u, region=+sphere1 | -sphere2)
geom = openmc.Geometry([cell1, cell2])
geom.export_to_xml()

# Finally, define some run settings
settings = openmc.Settings()
settings.batches = 200
settings.inactive = 10
settings.particles = 10000
settings.export_to_xml()

# Run the simulation
openmc.run()

# Get the resulting k-effective value
n = settings.batches
with openmc.StatePoint(f'statepoint.{n}.h5') as sp:
    keff = sp.keff
    print(f'Final k-effective = {keff}')
