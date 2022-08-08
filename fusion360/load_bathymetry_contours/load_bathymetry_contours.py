# Author-
# Description-
import os
import re
import math
import adsk.core, adsk.fusion, adsk.cam, traceback


def get_numbers_from_filename(filename):
    return re.search(r"\d+", filename).group(0)


def get_outer_profiles(profiles):
    # find target curve sizes which are holes
    hole_curve_sizes = set()
    for p in profiles:
        for pl in p.profileLoops:
            if not pl.isOuter:
                hole_curve_sizes.add(len(pl.profileCurves))

    # Only keep non hole profiles
    exterior_profiles = []
    for p in profiles:
        if (
            len(p.profileLoops) <= 1
            and len(p.profileLoops[0].profileCurves) in hole_curve_sizes
        ):
            continue
        exterior_profiles.append(p)
    return sorted(
        exterior_profiles, key=lambda p: p.areaProperties().area, reverse=True
    )


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        root = design.rootComponent

        title = "Import Contour SVGs"
        if not design:
            ui.messageBox("No active Fusion design", title)
            return

        # Get user params
        coaster_size_param = design.userParameters.itemByName("coaster_size")
        assert coaster_size_param, "missing user parameter: coaster_size"
        coaster_height_param = design.userParameters.itemByName("coaster_height")
        assert coaster_height_param, "missing user parameter: coaster_height"
        bathymetry_depth_param = design.userParameters.itemByName("bathymetry_depth")
        assert bathymetry_depth_param, "missing user parameter: bathymetry_depth_param"

        dlg = ui.createFileDialog()
        dlg.title = "Open Contour Folder"
        dlg.filter = "SVG (*.svg);;All Files (*.*)"
        dlg.isMultiSelectEnabled = True
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        svg_by_layer_idx = {
            int(get_numbers_from_filename(os.path.basename(f))): f
            for f in dlg.filenames
        }
        assert sorted(list(svg_by_layer_idx.keys())) == list(
            range(len(svg_by_layer_idx))
        ), f"Unexpected layer indices: {svg_by_layer_idx.keys()}"
        sorted_layer_fpaths = [
            svg_by_layer_idx[i] for i in sorted(svg_by_layer_idx.keys())
        ]

        progressDialog = ui.createProgressDialog()
        progressDialog.show(
            "Progress Dialog",
            "Percentage: %p, Current Layer: %v, Total Layers: %m",
            0,
            len(svg_by_layer_idx),
            1,
        )

        # Determine import scale
        svg_import_scale_param = design.userParameters.itemByName("svg_import_scale")
        if not svg_import_scale_param:
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.name = f"delete_me_test_for_scale"
            svg_fpath = sorted_layer_fpaths[0]
            assert sketch.importSVG(
                svg_fpath, 0, 0, 1.0
            ), f"Failed to import svg: {svg_fpath}"
            temp_profile = get_outer_profiles(sketch.profiles)[0]
            contour_short_dim = min(
                abs(
                    temp_profile.boundingBox.maxPoint.x
                    - temp_profile.boundingBox.minPoint.x
                ),
                abs(
                    temp_profile.boundingBox.maxPoint.y
                    - temp_profile.boundingBox.minPoint.y
                ),
            )
            svg_import_scale_param = design.userParameters.add(
                "svg_import_scale",
                adsk.core.ValueInput.createByReal(
                    coaster_size_param.value / contour_short_dim
                ),
                "cm",
                "The svg import scale",
            )
            sketch.deleteMe()
        import_scale = svg_import_scale_param.value

        # Create the sketches and bodies
        layer_sketches = []
        layer_bodies = []
        for layer_idx, svg_fpath in enumerate(sorted_layer_fpaths):
            # Update progress value of progress dialog
            progressDialog.progressValue = layer_idx

            # Create a sketch.
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.name = f"layer_{layer_idx}"
            assert sketch.importSVG(
                svg_fpath, 0, 0, import_scale
            ), f"Failed to import svg: {svg_fpath}"
            layer_sketches.append(sketch)

            exterior_profiles = get_outer_profiles(sketch.profiles)

            for profile_idx, profile in enumerate(exterior_profiles):
                e_input = root.features.extrudeFeatures.createInput(
                    profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
                e_input.setTwoSidesExtent(
                    adsk.fusion.DistanceExtentDefinition.create(
                        adsk.core.ValueInput.createByString(
                            # This expression should eval to: -layer_idx * layer_depth_cm
                            f"-{layer_idx}*{bathymetry_depth_param.name}/{len(sorted_layer_fpaths)}"
                        )
                    ),
                    adsk.fusion.DistanceExtentDefinition.create(
                        adsk.core.ValueInput.createByString(
                            # This expression should eval to: (layer_idx + 1) * layer_depth_cm
                            f"{layer_idx+1}*{bathymetry_depth_param.name}/{len(sorted_layer_fpaths)}"
                        )
                    ),
                )
                extrude = root.features.extrudeFeatures.add(e_input)
                for body_idx, body in enumerate(extrude.bodies):
                    body.name = (
                        f"layer_{layer_idx}_profile_{profile_idx}_body_{body_idx}"
                    )
                    layer_bodies.append(body)

        # Hide the progress dialog at the end.
        progressDialog.hide()

        # Combine the layer bodies
        if len(layer_bodies) >= 2:
            tool_bodies = adsk.core.ObjectCollection.create()
            for body in layer_bodies[1:]:
                tool_bodies.add(body)
            c_input = root.features.combineFeatures.createInput(
                layer_bodies[0], tool_bodies
            )
            c_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            c_input.isKeepToolBodies = False
            c_input.isNewComponent = False
            combination = root.features.combineFeatures.add(c_input)
            water_bodies = combination.bodies
        else:
            water_bodies = layer_bodies

        # Create the coaster sketch
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = "coaster"
        # water_centroid = (
        #     get_outer_profiles(layer_sketches[0].profiles)[0].areaProperties().centroid
        # )
        # sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        #     adsk.core.Point3D.create(
        #         water_centroid.x - coaster_size_param.value / 2,
        #         water_centroid.y + coaster_size_param.value / 2,
        #         0,
        #     ),
        #     adsk.core.Point3D.create(
        #         water_centroid.x + coaster_size_param.value / 2,
        #         water_centroid.y - coaster_size_param.value / 2,
        #         0,
        #     ),
        # )
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(
                coaster_size_param.value, -coaster_size_param.value, 0
            ),
        )
        extrude = root.features.extrudeFeatures.addSimple(
            sketch.profiles[0],
            adsk.core.ValueInput.createByString(f"-{coaster_height_param.name}"),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        )
        coaster_body = extrude.bodies[0]
        coaster_body.name = "coaster"

        # Cutout the coaster
        water_bodies_out = []
        tool_bodies = adsk.core.ObjectCollection.create()
        tool_bodies.add(coaster_body)
        for body in water_bodies:
            # Entirely outside... remove
            if not coaster_body.boundingBox.intersects(body.boundingBox):
                # water_bodies.remove(body)
                continue
            # Potentially needs intersect
            c_input = root.features.combineFeatures.createInput(body, tool_bodies)
            c_input.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
            c_input.isKeepToolBodies = True
            c_input.isNewComponent = False
            combination = root.features.combineFeatures.add(c_input)
            water_bodies_out.append(combination.bodies[0])
        water_bodies = water_bodies_out

        # Cutout the water
        tool_bodies = adsk.core.ObjectCollection.create()
        for body in water_bodies:
            tool_bodies.add(body)
        c_input = root.features.combineFeatures.createInput(coaster_body, tool_bodies)
        c_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        c_input.isKeepToolBodies = True
        c_input.isNewComponent = False
        combination = root.features.combineFeatures.add(c_input)
        coaster_body = combination.bodies[0]

        # Set materials
        appearance_lib = app.materialLibraries.itemByName(
            "Fusion 360 Appearance Library"
        )
        appearance_stone = appearance_lib.appearances.itemByName("Concrete")
        appearance_glass = appearance_lib.appearances.itemByName(
            "Glass - Medium Color (Blue)"
        )
        coaster_body.appearance = appearance_stone
        for body in water_bodies:
            body.appearance = appearance_glass
        app.activeViewport.refresh()

        ui.messageBox("Success")
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
