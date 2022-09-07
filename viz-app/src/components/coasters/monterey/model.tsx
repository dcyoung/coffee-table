import * as THREE from "three";
import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water.glb";
import MODEL_PATH_COASTER from "./coaster.glb";

export const CoasterMonterey = ({ ...props }): JSX.Element => CoasterBase({
    urlCoaster: MODEL_PATH_COASTER,
    urlsWater: [MODEL_PATH_WATER],
    importRotation: 0,
    orientationSequence: [
        (new THREE.Quaternion()).setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0),
        (new THREE.Quaternion()).setFromEuler(new THREE.Euler(0, Math.PI / 2, 0, "YXZ")),
        (new THREE.Quaternion()).setFromEuler(new THREE.Euler(-Math.PI / 2, Math.PI / 2, 0, "YXZ")),
        (new THREE.Quaternion()).setFromEuler(new THREE.Euler(-Math.PI / 2, Math.PI / 2, -Math.PI / 2, "YXZ")),
        (new THREE.Quaternion()).setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0),
    ],
    ...props,
});

export default CoasterMonterey;