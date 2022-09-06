import { useGLTF } from '@react-three/drei'

export declare interface ModelBaseProps {
    url: string;
}

export const ModelBase = ({
    url,
    ...props
}: ModelBaseProps): JSX.Element => {
    const { scene } = useGLTF(url);

    return (
        <primitive object={scene} {...props} />
    );
}

export default ModelBase;