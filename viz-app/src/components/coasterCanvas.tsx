import {
  ContactShadows,
  Environment,
  OrbitControls,
  ScrollControls,
} from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import CoasterTarget from "./coasterTarget";
import { LoadingOverlay } from "./loadingOverlay";

export declare interface CoasterCanvasProps {
  name: string;
  scrollable: boolean;
}

const CoasterCanvasContents = ({
  name,
  scrollable = false,
  ...props
}: CoasterCanvasProps): JSX.Element => {
  return (
    <>
      <Environment background={false} preset={"apartment"} />
      <CoasterTarget name={name} scrollable={scrollable}></CoasterTarget>
      <ContactShadows
        position={[0, -75, 0]}
        opacity={0.25}
        scale={500}
        blur={1.5}
        far={800}
      />
      {/* <Stats /> */}
    </>
  );
};

const CoasterCanvas = ({
  name,
  scrollable = false,
  ...props
}: CoasterCanvasProps): JSX.Element => {
  return (
    <Suspense fallback={null}>
      <Canvas
        shadows
        camera={{
          fov: 75,
          near: 0.1,
          far: 1000,
          position: [-75, 50, 50],
          up: [0, 1, 0],
        }}
      >
        {scrollable ? (
          <ScrollControls
            pages={5} // Each page takes 100% of the height of the canvas
            distance={1} // A factor that increases scroll bar travel (default: 1)
            damping={4} // Friction, higher is faster (default: 4)
            horizontal={false}
            infinite={false}
          >
            <CoasterCanvasContents name={name} scrollable={true} />
          </ScrollControls>
        ) : (
          <>
            <Suspense fallback={<LoadingOverlay />}>
              <CoasterCanvasContents name={name} scrollable={false} />
            </Suspense>
            <OrbitControls></OrbitControls>
          </>
        )}
      </Canvas>
    </Suspense>
  );
};

export default CoasterCanvas;
