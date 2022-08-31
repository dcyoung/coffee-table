# Author-
# Description-
import os
import re
import json
import numpy as np
from typing import List, Dict, Tuple
import adsk.core, adsk.fusion, adsk.cam, traceback


def poly_area(x: np.ndarray, y: np.ndarray) -> float:
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def contour_area(c: Dict, scale=1.0) -> float:
    return poly_area(
        x=scale * np.array([v[0] for v in c["simplified"]]),
        y=scale * np.array([v[1] for v in c["simplified"]]),
    )


def filter_raw_contours_by_area(
    contours: List[Dict], min_normalized_area: float
) -> List[Dict]:
    contours = [c for c in contours if contour_area(c) >= min_normalized_area]
    for c in contours:
        c["holes"] = [h for h in c["holes"] if contour_area(h) >= min_normalized_area]
    return contours


def bb_iou(bb1: adsk.core.BoundingBox3D, bb2: adsk.core.BoundingBox3D) -> float:
    if not bb1.intersects(bb2):
        return 0

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1.minPoint.x, bb2.minPoint.x)
    y_top = max(bb1.minPoint.y, bb2.minPoint.y)
    x_right = min(bb1.maxPoint.x, bb2.maxPoint.x)
    y_bottom = min(bb1.maxPoint.y, bb2.maxPoint.y)

    assert x_right > x_left and y_bottom > y_top

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1.maxPoint.x - bb1.minPoint.x) * (bb1.maxPoint.y - bb1.minPoint.y)
    bb2_area = (bb2.maxPoint.x - bb2.minPoint.x) * (bb2.maxPoint.y - bb2.minPoint.y)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert 0.0 <= iou <= 1.0
    return iou


def get_numbers_from_filename(filename: str) -> str:
    return re.search(r"\d+", filename).group(0)


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
                "The side length of a bounding box for in the imported contours.",
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

        layer_bodies = []
        progressDialog = ui.createProgressDialog()
        for layer_idx, fpath in enumerate(sorted_layer_fpaths):
            # Determine import scale
            sketch = root.sketches.add(root.xYConstructionPlane)
            sketch.name = f"layer_{layer_idx}"
            sk_lines = sketch.sketchCurves.sketchLines

            with open(fpath, "r") as f:
                contours = json.load(f)

            # remove tiny profiles if configured
            min_normalized_area = design.userParameters.itemByName(
                "min_contour_area_normalized"
            )
            if min_normalized_area:
                contours = filter_raw_contours_by_area(
                    contours=contours, min_normalized_area=min_normalized_area.value
                )

            def add_contour(contour) -> adsk.core.BoundingBox3D:
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

                bb = adsk.core.BoundingBox3D.create(vertices[0], vertices[1])
                for v in vertices[2:]:
                    assert bb.expand(v)
                return bb

            outer_contour_bounding_boxes = []
            for contour in contours:
                outer_contour_bounding_boxes.append(add_contour(contour))
                for hole in contour["holes"]:
                    add_contour(hole)

            def is_outer(p, tolerance: float = 0.01) -> bool:
                for bb in outer_contour_bounding_boxes:
                    if bb_iou(p.boundingBox, bb) >= (1 - tolerance):
                        return True

                return False

            exterior_profiles = sorted(
                [p for p in sketch.profiles if is_outer(p)],
                key=lambda p: p.areaProperties().area,
                reverse=True,
            )
            for profile_idx, profile in enumerate(exterior_profiles):
                # Draft extrusion can fail depending on shape of contour...
                # so repeat extrusion w/ binary search to find the working scalar <= 1.0
                last_known_working = 0.0
                last_known_failing = 2.0
                done = False
                while not done:
                    diff = abs(last_known_failing - last_known_working)
                    # mid point (binary search)
                    draft_scalar = last_known_working + (
                        diff / 2.0 if diff > 0.01 else 0
                    )
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
                    try:
                        extrude = root.features.extrudeFeatures.add(e_input)
                    except RuntimeError as e:
                        if "EXTRUDE_CREATION_FAIL_ERROR" in str(e):
                            # Failure case...
                            # try again w/ decreased draft angle
                            last_known_failing = draft_scalar
                            continue
                    if extrude.errorOrWarningMessage:
                        # Failure case...
                        # try again w/ decreased draft angle
                        extrude.deleteMe()
                        last_known_failing = draft_scalar
                        continue
                    elif draft_scalar < 1.0 and diff > 0.01:
                        # Success case... but could be better?
                        # Try again w/ increasing draft angle
                        try:
                            extrude.deleteMe()
                        except RuntimeError as e:
                            if "Assocated feature has been deleted." not in str(e):
                                raise e
                        last_known_working = draft_scalar
                        continue

                    for body_idx, body in enumerate(extrude.bodies):
                        body.name = (
                            f"layer_{layer_idx}_profile_{profile_idx}_body_{body_idx}"
                        )
                        layer_bodies.append(body)
                    break

        # Combine the layer bodies
        if len(sorted_layer_fpaths) >= 2 and len(layer_bodies):
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
