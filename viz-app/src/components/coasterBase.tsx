import { useGLTF } from '@react-three/drei'
// import { useFrame } from '@react-three/fiber';
// import { useRef } from 'react';
import { GLTF } from 'three/examples/jsm/loaders/GLTFLoader'

export interface CoasterBaseProps {
  urlCoaster: string;
  urlWater: string;
}

export const CoasterBase = ({
  urlCoaster,
  urlWater,
}: CoasterBaseProps): JSX.Element => {
  const gltfCoaster = useGLTF(urlCoaster);
  const gltfWater = useGLTF(urlWater);

  // useFrame(({ clock }) => {
  //   const elapsedTimeSec = clock.getElapsedTime();
  //   gltfWater.scene.position.y = 10 * (1 + Math.sin(0.5 * elapsedTimeSec));
  // });

  return (
    <group>
      <primitive object={(gltfCoaster as GLTF).scene} />
      <primitive object={(gltfWater as GLTF).scene} />
    </group>
  );
}


export default CoasterBase;