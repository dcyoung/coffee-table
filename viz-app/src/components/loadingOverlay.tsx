import { Html } from "@react-three/drei";
import "./spinner.css";
export declare interface LoadingOverlayProps {
    msg?: string;
}
export const LoadingOverlay = ({ msg = "Loading...", ...props }: LoadingOverlayProps): JSX.Element => {
    return (
        <Html as='div' center>
            <h1 style={{ color: 'black' }}>{msg}</h1>
            <svg className="spinner" viewBox="0 0 50 50">
                <circle className="path" cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle>
            </svg>
        </Html>
    );
}