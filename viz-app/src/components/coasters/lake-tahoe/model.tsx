import { Quaternion, Vector3 } from "three";
import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER_0 from "./water_0-draco.glb";
import MODEL_PATH_WATER_1 from "./water_1-draco.glb";
import MODEL_PATH_COASTER from "./coaster-draco.glb";

export const CoasterLakeTahoe = ({ ...props }): JSX.Element => CoasterBase({
    urls: [MODEL_PATH_COASTER, MODEL_PATH_WATER_0, MODEL_PATH_WATER_1], 
    importRotation: 0,
    orientation: (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
    ...props,
});

export default CoasterLakeTahoe;