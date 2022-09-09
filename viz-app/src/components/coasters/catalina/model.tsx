import * as THREE from "three";
import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water-draco.glb";
import MODEL_PATH_COASTER from "./coaster-draco.glb";

export const CoasterCatalina = ({ ...props }): JSX.Element => CoasterBase({
    urlCoaster: MODEL_PATH_COASTER,
    urlsWater: [MODEL_PATH_WATER],
    importRotation: 0,
    orientationSequence: [
        (new THREE.Quaternion()).setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0)
    ],
    ...props,
});

export default CoasterCatalina;