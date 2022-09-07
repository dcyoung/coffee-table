import React, { Suspense } from "react";

export declare interface CoasterTargetProps {
    name: string;
}

const getImportName = (name: string): string => {
    switch (name.toLowerCase()) {
        case "monterey":
        case "monterey-bay":
        case "monterey bay":
            return "monterey";
        case "catalina":
        case "catalina island":
            return "catalina";
        case "san-francisco bay":
        case "sf":
        case "sf-bay":
        case "san-francisco":
        case "san francisco":
            return "san-francisco-bay";
        case "lake tahoe":
        case "lake-tahoe":
        case "tahoe":
            return "lake-tahoe";
        default:
            throw new Error(`Unknown target ${name}`);
    }
}

export const CoasterTarget = ({ name, ...props }: CoasterTargetProps) => {
    const CoasterComponent = React.lazy(() => import(`./coasters/${getImportName(name)}/model`));
    return (
        <Suspense fallback={null}>
            <CoasterComponent {...props} />
        </Suspense>
    );
}


export default CoasterTarget;