import { useGLTF } from '@react-three/drei'
import { Suspense } from 'react';
import { GLTF } from 'three/examples/jsm/loaders/GLTFLoader'
import LoadingScreen from './loadingScreen';

export interface ModelBaseProps {
    url: string;
}

export const ModelBase = ({
    url,
    ...props
}: ModelBaseProps): JSX.Element => {
    const gltf = useGLTF(url);

    // useFrame(({ clock }) => {
    //   const elapsedTimeSec = clock.getElapsedTime();
    //   gltf.scene.position.y = 10 * (1 + Math.sin(0.5 * elapsedTimeSec));
    // });

    return (
        <Suspense fallback={<LoadingScreen></LoadingScreen>}>
            <primitive object={(gltf as GLTF).scene} {...props} />
        </Suspense>
    );
}

export default ModelBase;