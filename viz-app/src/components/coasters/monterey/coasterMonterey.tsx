import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water.glb";
import MODEL_PATH_COASTER from "./coaster.glb";

export const CoasterMonterey = (): JSX.Element => CoasterBase({
    urlCoaster: MODEL_PATH_COASTER, 
    urlWater: MODEL_PATH_WATER, 
});

export default CoasterMonterey;