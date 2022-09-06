import { CoasterBase } from "../../coasterBase";
import MODEL_PATH_WATER from "./water.glb";
import MODEL_PATH_COASTER from "./coaster.glb";

export const CoasterSanFranciscoBay = ({ ...props }): JSX.Element => {
    return <CoasterBase
        urlCoaster={MODEL_PATH_COASTER}
        urlsWater={[MODEL_PATH_WATER]}
        importRotation={Math.PI}
        {...props}
    ></CoasterBase>;
}


export default CoasterSanFranciscoBay;