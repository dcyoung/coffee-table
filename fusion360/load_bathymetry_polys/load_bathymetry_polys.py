# Author-
# Description-
import os
import re
import math
import json
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

        title = "Load Bathymetry Polys"
        if not design:
            ui.messageBox("No active Fusion design", title)
            return

        # Get user params
        coaster_size_param = design.userParameters.itemByName("coaster_size")
        if not coaster_size_param:
            coaster_size_param = design.userParameters.add(
                "coaster_size",
                adsk.core.ValueInput.createByString('4"'),
                "in",
                "The side length of the coaster",
            )
        contour_import_size_param = design.userParameters.itemByName(
            "contour_import_size"
        )
        if not contour_import_size_param:
            contour_import_size_param = design.userParameters.add(
                "contour_import_size",
                adsk.core.ValueInput.createByString(f"{coaster_size_param.name}"),
                "in",
                "The side length of the coaster",
            )
        coaster_height_param = design.userParameters.itemByName("coaster_height")
        if not coaster_height_param:
            coaster_height_param = design.userParameters.add(
                "coaster_height",
                adsk.core.ValueInput.createByString("0.5"),
                "in",
                "The height of the coaster",
            )
        bathymetry_depth_param = design.userParameters.itemByName("bathymetry_depth")
        if not bathymetry_depth_param:
            bathymetry_depth_param = design.userParameters.add(
                "bathymetry_depth",
                adsk.core.ValueInput.createByString(f"0.8*{coaster_height_param.name}"),
                "in",
                "The depth of the combined bathymetry contours.",
            )
        draft_angle_param = design.userParameters.itemByName("draft_angle")
        if not draft_angle_param:
            draft_angle_param = design.userParameters.add(
                "draft_angle",
                adsk.core.ValueInput.createByString("5deg"),
                "deg",
                "The draft angle for extruded contours.",
            )

        dlg = ui.createFileDialog()
        dlg.title = "Open Contour Folder"
        dlg.filter = "JSON (*.json);;All Files (*.*)"
        dlg.isMultiSelectEnabled = True
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        fpath_by_layer_idx = {
            int(get_numbers_from_filename(os.path.basename(f))): f
            for f in dlg.filenames
        }
        assert sorted(list(fpath_by_layer_idx.keys())) == list(
            range(len(fpath_by_layer_idx))
        ), f"Unexpected layer indices: {fpath_by_layer_idx.keys()}"
        sorted_layer_fpaths = [
            fpath_by_layer_idx[i] for i in sorted(fpath_by_layer_idx.keys())
        ]

        def vert2point(v):
            return adsk.core.Point3D.create(
                contour_import_size_param.value * v[0],
                -contour_import_size_param.value * v[1],
                0,
            )

        layer_sketches = []
        layer_bodies = []
        progressDialog = ui.createProgressDialog()
        for layer_idx, fpath in enumerate(sorted_layer_fpaths):
            # Determine import scale
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.name = f"layer_{layer_idx}"
            sk_lines = sketch.sketchCurves.sketchLines

            with open(fpath, "r") as f:
                contours = json.load(f)

            def add_contour(contour):
                vertices = [vert2point(v) for v in contour["simplified"]]
                progressDialog.show(
                    "Progress Dialog",
                    "Percentage: %p, Current Vertex: %v, Total Vertices: %m",
                    0,
                    len(vertices),
                    1,
                )

                line_start = sk_lines.addByTwoPoints(vertices[0], vertices[1])
                prev_line = line_start
                for i, v in enumerate(vertices[2:]):
                    prev_line = sk_lines.addByTwoPoints(prev_line.endSketchPoint, v)
                    progressDialog.progressValue = i
                sk_lines.addByTwoPoints(
                    prev_line.endSketchPoint, line_start.startSketchPoint
                )

                progressDialog.hide()

            for contour in contours:
                add_contour(contour)
                for hole in contour["holes"]:
                    add_contour(hole)

            layer_sketches.append(sketch)
            exterior_profiles = get_outer_profiles(sketch.profiles)
            for profile_idx, profile in enumerate(exterior_profiles):
                # Draft extrusion can fail depending on shape of contour... so repeat extrude on failure w/ smaller draft angle
                for draft_scalar in [1.0, 0.75, 0.5, 0.25, 0.1, 0.0]:
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
                        adsk.core.ValueInput.createByReal(0),
                        adsk.core.ValueInput.createByString(
                            f"-{draft_scalar}*{draft_angle_param.name}"
                        ),
                    )
                    extrude = root.features.extrudeFeatures.add(e_input)
                    if extrude.errorOrWarningMessage:
                        extrude.deleteMe()
                        continue
                    for body_idx, body in enumerate(extrude.bodies):
                        body.name = (
                            f"layer_{layer_idx}_profile_{profile_idx}_body_{body_idx}"
                        )
                        layer_bodies.append(body)
                    break

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
