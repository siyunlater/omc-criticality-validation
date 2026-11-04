import openmc

# Create plutonium metal material
u = openmc.Material()
u.set_density('sum')
u.add_nuclide('U233', 4.6712e-02)
u.add_nuclide('U234', 5.9026e-04)
u.add_nuclide('U235', 1.4281e-05)
u.add_nuclide('U238', 2.8561e-04)
mats = openmc.Materials([u])
mats.export_to_xml()

# Create a single cell filled with the Pu metal
sphere = openmc.Sphere(r=5.9838, boundary_type='vacuum')
cell = openmc.Cell(fill=u, region=-sphere)
geom = openmc.Geometry([cell])
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
