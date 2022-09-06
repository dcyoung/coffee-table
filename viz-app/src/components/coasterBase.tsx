import { Suspense, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import ModelBase from "./modelBase";

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
}

export const CoasterBase = ({
  urlCoaster,
  urlsWater,
  importRotation = 0.0,
  ...props
}: CoasterBaseProps): JSX.Element => {
  const coaster = useRef<THREE.Group>(null!);

  useFrame(({ clock }) => {
    if (!coaster.current) {
      return;
    }
    const t = clock.getElapsedTime()
    coaster.current.rotation.z = THREE.MathUtils.lerp(coaster.current.rotation.z, Math.cos(t / 2) / 20 + 0.25, 0.1)
    coaster.current.rotation.y = THREE.MathUtils.lerp(coaster.current.rotation.y, Math.sin(t / 4) / 20, 0.1)
    coaster.current.rotation.x = THREE.MathUtils.lerp(coaster.current.rotation.x, Math.sin(t / 8) / 20, 0.1)
    coaster.current.position.y = THREE.MathUtils.lerp(coaster.current.position.y, (-2 + Math.sin(t / 2)) / 2, 0.1)
  })

  return (
    <group ref={coaster} {...props}>
      <Suspense fallback={<CoasterModelPlaceholder></CoasterModelPlaceholder>}>
        <ModelBase url={urlCoaster} rotation-y={importRotation}></ModelBase>
        {
          urlsWater.map((url) => { return <ModelBase url={url} rotation-y={importRotation}></ModelBase> })
        }
      </Suspense>
    </group>
  );
}

export default CoasterBase;