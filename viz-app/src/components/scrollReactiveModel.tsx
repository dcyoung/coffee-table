import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Euler, Group, Quaternion } from "three";
import { useScroll } from "@react-three/drei";

export declare interface ScrollReactiveModelProps {
    orientationSequence: Quaternion[];
    children?: React.ReactNode;
}

export const ScrollReactiveModel = ({
    orientationSequence = [
        (new Quaternion()).setFromEuler(new Euler(0, 0, 0))
    ],
    children = null,
    ...props
}: ScrollReactiveModelProps): JSX.Element => {
    const modelRef = useRef<Group>(null!);
    const currOrientation = (new Quaternion()).copy(orientationSequence[0]);
    const scroll = useScroll();

    useFrame(({ clock }) => {
        if (modelRef == null || !modelRef.current) {
            return;
        }

        const nPages = orientationSequence.length - 1;
        if (nPages <= 0) {
            modelRef.current.setRotationFromQuaternion(currOrientation);
            return;
        }

        const distPerPage = 1 / nPages;
        // scroll.offset = current scroll position, between 0 and 1, dampened
        // scroll.delta = current delta, between 0 and 1, dampened
        orientationSequence.forEach((targetOrientation, orientationIdx) => {
            const pageIdx = orientationIdx - 1;
            const start = pageIdx / nPages;
            if (start < 0 || !scroll.visible(start, distPerPage)) {
                return;
            }

            const prevOrientation = orientationSequence[orientationIdx - 1];
            const progress = scroll.range(start, distPerPage);

            // Set orientation based on scroll
            currOrientation.slerpQuaternions(prevOrientation, targetOrientation, progress);
            modelRef.current.setRotationFromQuaternion(currOrientation);
        });
    })

    return (
        <group ref={modelRef} {...props}>
            {children}
        </group>
    );
}

export default ScrollReactiveModelProps;