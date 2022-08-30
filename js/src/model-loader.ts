import * as THREE from 'three';

function shapeFromVerts(vertices: Array<Array<number>>): THREE.Shape {
    const vRoot = vertices[0];
    const shape = new THREE.Shape();
    shape.moveTo(vRoot[0], vRoot[1]);
    for (const v of vertices.slice(1)) {
        shape.lineTo(v[0], v[1]);
    }
    shape.lineTo(vRoot[0], vRoot[1]);
    return shape;
}

class BathymetryContourGeometriesLoader extends THREE.Loader {
    constructor(manager: THREE.LoadingManager) {
        super(manager);
    }

    async loadShapesBylayerAsync(url: string): Promise<THREE.Shape[][]> {
        let shapesByLayer: THREE.Shape[][] = [];
        let layerIdx = 0;
        while (true) {
            const response = await fetch(`${url}/layer_${layerIdx}_contours.json`);
            if (!response.ok) {
                break;
            }
            const shapesForLayer = [];
            const contours = await response.json();
            for (const contour of contours) {
                const shape = shapeFromVerts(contour.simplified);
                for (const h of contour.holes) {
                    shape.holes.push(shapeFromVerts(h.simplified));
                }
                shapesForLayer.push(shape);
            }
            shapesByLayer.push(shapesForLayer)
            layerIdx++;
        }
        return shapesByLayer;
    }

    loadContourGeometriesByLayer(shapesByLayer: THREE.Shape[][], maxWaterDepth: number): THREE.ExtrudeGeometry[][] {
        const extrudeSettings = {
            steps: 1,
            depth: maxWaterDepth / shapesByLayer.length,
            bevelEnabled: false,
        };
        const contourGeometriesByLayer = [];
        for (let layerIdx = 0; layerIdx < shapesByLayer.length; layerIdx++) {
            const contourGeometries = [];
            for (const shape of shapesByLayer[layerIdx]) {
                const contourGeometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                // Center and offset for layer index
                contourGeometry.translate(-0.5, -0.5, layerIdx * extrudeSettings.depth);
                contourGeometries.push(contourGeometry);
            }
            contourGeometriesByLayer.push(contourGeometries);
        }
        return contourGeometriesByLayer;
    }

    load(
        url: string,
        maxWaterDepth: number,
        onLoad: (contourGeometriesByLayer: THREE.ExtrudeGeometry[][]) => void,
        onError?: (event: ErrorEvent) => void,
    ): void {
        this.loadShapesBylayerAsync(url).then((shapesByLayer) => {
            const contourGeometriesByLayer = this.loadContourGeometriesByLayer(shapesByLayer, maxWaterDepth);
            onLoad(contourGeometriesByLayer);
        }).catch(err => {
            onError(err);
            this.manager.itemError(url);

        }).finally(() => {
            this.manager.itemEnd(url);
        })
        this.manager.itemStart(url);
    }
}

export { BathymetryContourGeometriesLoader };