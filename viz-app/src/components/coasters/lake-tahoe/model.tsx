import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER_0 from "./water_0.glb";
import MODEL_PATH_WATER_1 from "./water_1.glb";
import MODEL_PATH_COASTER from "./coaster.glb";

export const CoasterLakeTahoe = ({ ...props }): JSX.Element => CoasterBase({
    urlCoaster: MODEL_PATH_COASTER, 
    urlsWater: [MODEL_PATH_WATER_0, MODEL_PATH_WATER_1], 
    importRotation: 0,
    ...props,
});

export default CoasterLakeTahoe;