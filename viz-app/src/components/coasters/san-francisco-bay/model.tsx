import { Quaternion, Vector3 } from "three";
import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water-draco.glb";
import MODEL_PATH_COASTER from "./coaster-draco.glb";

export const CoasterSanFranciscoBay = ({ ...props }): JSX.Element =>
  CoasterBase({
    urls: [MODEL_PATH_COASTER, MODEL_PATH_WATER],
    importRotation: Math.PI,
    orientation: new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), 0),
    ...props,
  });

export default CoasterSanFranciscoBay;
