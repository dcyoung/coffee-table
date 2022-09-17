import * as THREE from "three";
import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water-draco.glb";
import MODEL_PATH_COASTER from "./coaster-draco.glb";

export const CoasterMonterey = ({ ...props }): JSX.Element => CoasterBase({
    urls: [MODEL_PATH_COASTER, MODEL_PATH_WATER],
    importRotation: 0,
    orientation: (new THREE.Quaternion()).setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0),
    ...props,
});

export default CoasterMonterey;