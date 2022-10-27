import { Suspense, useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import ModelBase from "./modelBase";
import { Clock, Group, Quaternion, Vector3 } from "three";
import { LoadingOverlay } from "./loadingOverlay";

export const CoasterModelPlaceholder = ({ ...props }): JSX.Element => {
  return (
    <mesh {...props}>
      <boxGeometry args={[101.6, 12.7, 101.6]}></boxGeometry>
      <meshStandardMaterial color={'beige'} />
      <LoadingOverlay msg="Loading..." />
    </mesh>
  );
}

export declare interface CoasterBaseProps {
  urls: string[];
  importRotation: number;
  orientation: Quaternion;
}

export const CoasterBase = ({
  urls,
  importRotation = 0.0,
  orientation = (new Quaternion()).setFromAxisAngle(new Vector3(0, 1, 0), 0),
  ...props
}: CoasterBaseProps): JSX.Element => {
  const coaster = useRef<Group>(null!);

  const hover = (clock: Clock) => {
    // add slight hover effect
    const t = clock.getElapsedTime()
    const amplitude = 0.0005;
    coaster.current.position.y += amplitude * Math.sin(1 * t);
    coaster.current.rotation.z += amplitude * Math.cos(0.5 * t);
    coaster.current.rotation.y += amplitude * Math.cos(0.7 * t);
  }

  useFrame(({ clock }) => {
    if (!coaster.current) {
      return;
    }
    hover(clock);
  })

  useEffect(() => {
    coaster.current.setRotationFromQuaternion(orientation)
  }, [orientation])

  return (
    <group ref={coaster} {...props}>
      {
        urls.length > 0
          ? (
            <Suspense fallback={<CoasterModelPlaceholder />}>
              {
                urls.map((url, idx) => {
                  return <ModelBase
                    url={url}
                    key={`model-${idx}`}
                    rotation-y={importRotation}></ModelBase>;
                })
              }
            </Suspense>
          )
          : <CoasterModelPlaceholder />}
    </group>
  );
}

export default CoasterBase;