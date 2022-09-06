import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water.glb";
import MODEL_PATH_COASTER from "./coaster.glb";

export const CoasterCatalina = ({ ...props }): JSX.Element => CoasterBase({
    urlCoaster: MODEL_PATH_COASTER, 
    urlsWater: [MODEL_PATH_WATER], 
    importRotation: 0,
    ...props,
});

export default CoasterCatalina;