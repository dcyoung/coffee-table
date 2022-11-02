import { Quaternion, Vector3 } from "three";
import { CoasterBase } from "../coasterBase";

export const CoasterPlaceholder = ({ ...props }): JSX.Element =>
  CoasterBase({
    urls: [],
    importRotation: 0,
    orientation: new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), 0),
    ...props,
  });

export default CoasterPlaceholder;
