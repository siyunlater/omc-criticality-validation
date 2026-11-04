import openmc

# Create plutonium metal material
# Godiva
# 1D sphere
# bare
# high enriched uranium
# critical benchmark

u = openmc.Material()
u.set_density('sum') #u.set_density('') [g.cm-3] weight density
u.add_nuclide('U234', 4.9184e-04)
u.add_nuclide('U235', 4.4994e-02)
u.add_nuclide('U238', 2.4984e-03)
mats = openmc.Materials([u])
mats.export_to_xml()

# Create a single cell filled with the Pu metal
sphere = openmc.Sphere(r=8.7407, boundary_type='vacuum')
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
