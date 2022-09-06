import CoasterMonterey from "./coasters/monterey/model";
import CoasterCatalina from "./coasters/catalina/model";

export interface CoasterTargetProps {
    name: string;
}

export const CoasterTarget = ({
    name,
    ...props
}: CoasterTargetProps): JSX.Element => {
    switch (name.toLowerCase()) {
        case "monterey":
            return <CoasterMonterey {...props}></CoasterMonterey>;
        case "catalina":
            return <CoasterCatalina {...props}></CoasterCatalina>;
        default:
            throw new Error(`Unknown target ${name}`);
    }
}

export default CoasterTarget;