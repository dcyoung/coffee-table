import { Suspense, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import ModelBase from "./modelBase";
import { useScroll } from "@react-three/drei";

export const CoasterModelPlaceholder = ({ ...props }): JSX.Element => {
  return (
    <mesh {...props}>
      <boxGeometry args={[101.6, 12.7, 101.6]}></boxGeometry>
      <meshStandardMaterial color={'beige'} />
    </mesh>
  );
}

export declare interface CoasterBaseProps {
  urlCoaster: string;
  urlsWater: string[];
  importRotation: number;
  orientationSequence: THREE.Quaternion[];
}

export const CoasterBase = ({
  urlCoaster,
  urlsWater,
  importRotation = 0.0,
  orientationSequence = [
    (new THREE.Quaternion()).setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0)
  ],
  ...props
}: CoasterBaseProps): JSX.Element => {
  const currOrientation = (new THREE.Quaternion()).copy(orientationSequence[0]);
  const coaster = useRef<THREE.Group>(null!);
  const scroll = useScroll();

  const hover = (clock: THREE.Clock) => {
    // add slight hover effect
    const t = clock.getElapsedTime()
    coaster.current.position.y += 0.01 * Math.sin(1 * t);
    coaster.current.rotation.z += 0.01 * Math.cos(0.5 * t);
    coaster.current.rotation.y += 0.01 * Math.cos(0.7 * t);
  }

  useFrame(({ clock }) => {
    if (!coaster.current) {
      return;
    }

    const nPages = orientationSequence.length - 1;
    if (nPages <= 0) {
      coaster.current.setRotationFromQuaternion(currOrientation);
      hover(clock);
      return;
    }
    
    const distPerPage = 1 / nPages;
    // scroll.offset = current scroll position, between 0 and 1, dampened
    // scroll.delta = current delta, between 0 and 1, dampened
    orientationSequence.forEach((targetOrientation, orientationIdx) => {
      const pageIdx = orientationIdx -1;
      const start = pageIdx / nPages;
      if (start < 0 || !scroll.visible(start, distPerPage)){
        return;
      }

      const prevOrientation = orientationSequence[orientationIdx - 1];
      const progress = scroll.range(start, distPerPage);
      
      // Set orientation based on scroll
      currOrientation.slerpQuaternions(prevOrientation, targetOrientation, progress);
      coaster.current.setRotationFromQuaternion(currOrientation);
      hover(clock);
    });
  })

  return (
    <group ref={coaster} {...props}>
      <Suspense fallback={<CoasterModelPlaceholder></CoasterModelPlaceholder>}>
        <ModelBase url={urlCoaster} rotation-y={importRotation}></ModelBase>
        {
          urlsWater.map((url, idx) => {
            return <ModelBase
              url={url}
              key={`water-model-${idx}`}
              rotation-y={importRotation}></ModelBase>;
          })
        }
      </Suspense>
    </group>
  );
}

export default CoasterBase;