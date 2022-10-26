import React, { Suspense } from "react";
import { Euler, Quaternion, Vector3 } from "three";
import CoasterPlaceholder from "./coasters/placeholder";
import { ScrollReactiveModel } from "./scrollReactiveModel";

const IMPORT_NAME_CATALINA = "catalina";
const IMPORT_NAME_SF = "san-francisco-bay";
const IMPORT_NAME_LAKE_TAHOE = "lake-tahoe";
const IMPORT_NAME_MONTEREY = "monterey";


const getImportName = (name: string): string => {
    switch (name.toLowerCase()) {
        case "monterey":
        case "monterey-bay":
        case "monterey bay":
            return IMPORT_NAME_MONTEREY;
        case "catalina":
        case "catalina island":
            return IMPORT_NAME_CATALINA;
        case "san-francisco bay":
        case "sf":
        case "sf-bay":
        case "san-francisco":
        case "san francisco":
            return IMPORT_NAME_SF;
        case "lake tahoe":
        case "lake-tahoe":
        case "tahoe":
            return IMPORT_NAME_LAKE_TAHOE;
        default:
            throw new Error(`Unknown target ${name}`);
    }
}

const getScrollOrientationSequence = (importName: string): Quaternion[] => {
    switch (importName) {
        case IMPORT_NAME_MONTEREY:
            return [
                (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
                (new Quaternion()).setFromEuler(new Euler(0, Math.PI / 2, 0, "YXZ")),
                (new Quaternion()).setFromEuler(new Euler(-Math.PI / 2, Math.PI / 2, 0, "YXZ")),
                (new Quaternion()).setFromEuler(new Euler(-Math.PI / 2, Math.PI / 2, -Math.PI / 2, "YXZ")),
                (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
            ];
        case IMPORT_NAME_SF:
            return [
                (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
                (new Quaternion()).setFromEuler(new Euler(0, 0, Math.PI / 2, "ZYX")),
                (new Quaternion()).setFromEuler(new Euler(Math.PI / 2, 0, Math.PI / 2, "ZYX")),
                (new Quaternion()).setFromEuler(new Euler(0, Math.PI / 2, 0, "YXZ")),
                (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
            ]
        default:
            return [
                (new Quaternion()).setFromEuler(new Euler(0, 0, 0))
            ];
    }
}

export declare interface CoasterTargetProps {
    name: string;
    scrollable?: boolean;
}

const CoasterTarget = ({ name, scrollable = false, ...props }: CoasterTargetProps) => {
    const importName = getImportName(name);
    const CoasterComponent = React.lazy(() => import(`./coasters/${importName}/model.tsx`));
    return (
        <Suspense fallback={<CoasterPlaceholder {...props} />}>
            {scrollable
                ? (
                    <ScrollReactiveModel
                        orientationSequence={
                            getScrollOrientationSequence(importName)
                        }>
                        <CoasterComponent {...props} />
                    </ScrollReactiveModel>
                )
                : <CoasterComponent {...props} />
            }
        </Suspense>
    );
}


export default CoasterTarget;