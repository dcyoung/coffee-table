# Author-
# Description-
import json
import adsk.core, adsk.fusion, adsk.cam, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        root = design.rootComponent

        title = "Load Bathymetry Poly - Single"
        if not design:
            ui.messageBox("No active Fusion design", title)
            return

        dlg = ui.createFileDialog()
        dlg.title = "Open Contour Folder"
        dlg.filter = "JSON (*.json);;All Files (*.*)"
        dlg.isMultiSelectEnabled = False
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        def vert2point(v):
            size = 4 * 2.54  # 4" in cm
            return adsk.core.Point3D.create(size * v[0], -size * v[1], 0)

        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = f"test"
        sk_lines = sketch.sketchCurves.sketchLines
        with open(dlg.filename, "r") as f:
            contours = json.load(f)

        def add_contour(contour):
            vertices = [vert2point(v) for v in contour["simplified"]]
            line_start = sk_lines.addByTwoPoints(vertices[0], vertices[1])
            prev_line = line_start
            for i, v in enumerate(vertices[2:]):
                prev_line = sk_lines.addByTwoPoints(prev_line.endSketchPoint, v)
            sk_lines.addByTwoPoints(
                prev_line.endSketchPoint, line_start.startSketchPoint
            )

        for contour in contours:
            add_contour(contour)
            for hole in contour["holes"]:
                add_contour(hole)
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
