import argparse

from magnum import *
from magnum import trade
from magnum import math as mmath

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')
parser.add_argument('-v', '--verbose', action='store_true') # Try this!
args = parser.parse_args()

# Scene conversion plugins need access to image conversion plugins
image_converter_manager = trade.ImageConverterManager()
scene_converter_manager = trade.SceneConverterManager()
scene_converter_manager.register_external_manager(image_converter_manager)

# Load the plugins
importer = trade.ImporterManager().load_and_instantiate('AnySceneImporter')
converter = scene_converter_manager.load_and_instantiate('AnySceneConverter')
meshoptimizer = trade.SceneConverterManager().load_and_instantiate('MeshOptimizerSceneConverter')
if args.verbose:
    importer.flags |= trade.ImporterFlags.VERBOSE
    converter.flags |= trade.SceneConverterFlags.VERBOSE
    meshoptimizer.flags |= trade.SceneConverterFlags.VERBOSE

# Meshoptimizer defaults. You might want to play with these, see plugin docs
# for more info: https://doc.magnum.graphics/magnum/classMagnum_1_1Trade_1_1MeshOptimizerSceneConverter.html
meshoptimizer.configuration['simplify'] = True
# You might want to enable this on a per-mesh basis, if the non-sloppy
# simplification fails to reach the target by a wide margin
meshoptimizer.configuration['simplifySloppy'] = True
# This might be too harsh if you want to preserve fine details
meshoptimizer.configuration['simplifyTargetError'] = 1.0e-1
# Magic!!!
the_magic_constant = 42*42*4

# glTF converter defaults, using JPEGs instead of PNGs for smaller file size.
# Again, check docs or
#  magnum-sceneconverter -C GltfSceneConverter --info-converter
# for all options.
converter.configuration['imageConverter'] = 'JpegImageConverter'

importer.open_file(args.input)
converter.begin_file(args.output)

# Go through all meshes and decimate them
size_before = 0
size_after = 0
for i in range(importer.mesh_count):
    mesh = importer.mesh(i)

    # Calculate total triangle area. You might want to fiddle with this
    # heuristics, another option is calculating the mesh AABB but that won't
    # do the right thing for planar meshes.
    if not mesh.is_indexed:
        assert False, "i didn't bother with index-less variant for the heuristics, sorry"
    if mesh.primitive != MeshPrimitive.TRIANGLES:
        assert False, "i didn't bother with non-triangle meshes either, sorry"
    triangle_count = mesh.index_count//3
    total_area = 0.0
    indices = mesh.indices
    positions = mesh.attribute(trade.MeshAttribute.POSITION)
    for j in range(triangle_count):
        # This is stupidly slow, wth python?!
        a: Vector3 = positions[indices[j*3 + 0]]
        b: Vector3 = positions[indices[j*3 + 1]]
        c: Vector3 = positions[indices[j*3 + 2]]

        # Triangle area is half of the cross product of its two vectors
        total_area += mmath.cross(b - a, c - a).length()*0.5

    # Simplify & optimize the mesh. Might want to skip simplification if target
    # is close to 1.
    target = the_magic_constant/(triangle_count/total_area)
    meshoptimizer.configuration['simplifyTargetIndexCountThreshold'] = target
    decimated_mesh = meshoptimizer.convert(mesh)

    # Stats
    print("Mesh {} tri count / area: {:10.1f}; target: {:1.4f}; result: {:1.4f}".format(i, triangle_count/total_area, target, decimated_mesh.index_count/mesh.index_count))
    size_before += len(mesh.index_data) + len(mesh.vertex_data)
    size_after += len(decimated_mesh.index_data) + len(decimated_mesh.vertex_data)

    # Add it to the converter, preserve its name
    converter.add(decimated_mesh, name=importer.mesh_name(i))

print("Mesh size reduction: {:.1f}K -> {:.1f}K ({:.2f}%)".format(size_before/1000, size_after/1000, 100*size_after/size_before))

# Add also everything else except the meshes and ... done!
converter.add_importer_contents(importer, ~trade.SceneContents.MESHES)
converter.end_file()

print("Saved to {}".format(args.output))
