import adsk.core, adsk.fusion, adsk.cam, traceback
import csv

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # Cuadro de diálogo para seleccionar el archivo CSV
        fileDialog = ui.createFileDialog()
        fileDialog.isMultiSelectEnabled = False
        fileDialog.title = "Selecciona el archivo CSV"
        fileDialog.filter = "*.csv"
        dialogResult = fileDialog.showOpen()

        if dialogResult == adsk.core.DialogResults.DialogOK:
            filePath = fileDialog.filename
        else:
            ui.messageBox("No se seleccionó ningún archivo")
            return

        # Leer los datos del archivo CSV
        points = {}
        with open(filePath, 'r') as file:
            csvReader = csv.reader(file)
            next(csvReader)  # Omitir la cabecera
            for row in csvReader:
                sketch_id, plane, x, y, z = row[0], row[1], float(row[2]), float(row[3]), float(row[4])
                if sketch_id not in points:
                    points[sketch_id] = {'plane': plane, 'points': []}
                points[sketch_id]['points'].append((x, y, z))

        # Crear bocetos para cada grupo de puntos
        sketches = rootComp.sketches
        plane_map = {'XY': rootComp.xYConstructionPlane, 'XZ': rootComp.xZConstructionPlane, 'YZ': rootComp.yZConstructionPlane}

        for sketch_id, data in points.items():
            point_list = data['points']
            plane = data['plane']
            if not point_list or plane not in plane_map:
                continue

            # Crear un nuevo boceto en el plano especificado
            sketch_plane = plane_map[plane]
            sketch = sketches.add(sketch_plane)

            # Transformar puntos según el plano
            if plane == 'XY':
                transformed_points = [adsk.core.Point3D.create(x, y, z) for x, y, z in point_list]
            elif plane == 'XZ':
                transformed_points = [adsk.core.Point3D.create(x, z, y) for x, y, z in point_list]
            elif plane == 'YZ':
                transformed_points = [adsk.core.Point3D.create(y, z, x) for x, y, z in point_list]

            # Dibujar líneas que conecten los puntos en el boceto
            for i in range(len(transformed_points) - 1):
                sketch.sketchCurves.sketchLines.addByTwoPoints(transformed_points[i], transformed_points[i + 1])

        ui.messageBox("Bocetos creados con éxito")

    except Exception as e:
        if ui:
            ui.messageBox(f"Failed:\n{traceback.format_exc()}")
